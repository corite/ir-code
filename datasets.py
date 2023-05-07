import os
from os.path import join
from torch.utils.data import Dataset
import imageio.v3 as iio
import numpy as np
from bs4 import BeautifulSoup
from functools import cached_property
from dataclasses import dataclass
import logging
import pandas as pd
from pyterrier.datasets import Dataset as PTDataset
from tqdm import tqdm
import json
from neville.text_extractor import extract_content

logger = logging.getLogger(__name__)

class ToucheDataset(PTDataset):
    
    def __init__(self, topics_file, corpus_dir, qrels_file=None):
        self.images = ToucheImageDataset(corpus_dir)
        self.topics = ToucheTopics(topics_file)
        self.qrels_file = qrels_file
        
    def get_topics(self):
        return self.topics.to_pandas()
    
    def get_qrels(self, variant):
        if not self.qrels_file:
            print('No qrels passed in constructor, returning empty DataFrame')
            return pd.DataFrame(columns=['qid', 'stance', 'docno', 'label'])
        variant = variant.upper()
        if variant not in ['PRO', 'CON', 'LABLED']:
            raise Exception('Please specify if PRO or CON documents should be labeled relevant by passing the respective variant argument')
        qrels_touche = pd.read_csv(self.qrels_file, sep='\s+', names=['qid', 'stance', 'docno', 'label'], dtype={'qid': str, 'label': int})
        if variant != 'LABLED':
            return qrels_touche[qrels_touche['stance'] == variant].drop(columns=['stance'])
        else:
            return qrels_touche.drop(columns='stance').assign(label=1)

    def get_corpus_iter(self, verbose=True):
        iterator = ({
            'docno': image.name,
            'image_id': image.id,
            'text': image.page.snapshot_cleaned
        } for image in self.images)
        
        if verbose:
            return tqdm(iterator, total=len(self.images))
        else:
            return iterator
        
    def get_image_text_iter(self, verbose=True):
        iterator = ({
            'docno': image.name,
            'image_id': image.id,
            'text': ' '.join(extract_content(image))
        } for image in self.images)
        
        if verbose:
            return tqdm(iterator, total=len(self.images))
        else:
            return iterator
        
@dataclass
class Topic:
    number: int
    title: str
    description: str
    narrative: str

class ToucheTopics(dict):
    
    def __init__(self, topics_file):
        if topics_file.endswith('.jsonl'):
            with open(topics_file, 'r') as f:
                for line in f:
                    query_json = json.loads(line)
                    num = int(query_json['qid'])
                    self[num] = Topic(
                        number=num,
                        title=query_json['query'],
                        description=None,
                        narrative=None)
        elif topics_file.endswith('.xml'):
            with open(topics_file, 'r') as f:
                soup = BeautifulSoup(f.read(), 'xml')
                for topic in soup.find_all('topic'):
                    num = int(topic.number.text)
                    self[num] = Topic(
                        number=num,
                        title=topic.title.text.strip(),
                        description=topic.description.text.strip(),
                        narrative=topic.narrative.text.strip()
                    )
        else:
            raise Exception('Unsupported file type, extension is neither .jsonl nor .xml')
        
    def to_pandas(self):
        records = map(lambda t: {'id': t.number, 'qid': str(t.number), 'query': t.title}, self.values())
        return pd.DataFrame(records).set_index('id')

class ToucheImageDataset(Dataset):
    
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.image_ids = []
        
        for img_group_dir in os.scandir(self.root_dir):
            if img_group_dir.is_dir():
                for img_dir in os.scandir(img_group_dir.path):
                    if img_dir.is_dir():
                        self.image_ids.append(img_dir.name)
        self.image_ids.sort()

    def __len__(self):
        return len(self.image_ids)
    
    def __getitem__(self, idx):
        if isinstance(idx, str):
            return self[self.image_ids.index(idx)]
        elif isinstance(idx, slice):
            return [self[i] for i in range(*idx.indices(len(self)))]
        else:
            idx = int(idx)
            image_id = self.image_ids[idx]
            return Image(idx, image_id, join(self.root_dir, image_id[:3], image_id))
    
class Image:
    
    def __init__(self, img_id, img_name, img_dir):
        self.id = img_id
        self.name = img_name
        self.img_dir = img_dir
        
    @cached_property
    def url(self):
        with open(join(self.img_dir, 'image-url.txt'), 'r') as f:
            return f.read().rstrip()
        
    @cached_property
    def page(self):
        page_dir = next(filter(lambda f: f.is_dir(), os.scandir(join(self.img_dir, 'pages'))))
        return Page(page_dir)
    
    def find_occurences_in_page(self):
        return self.page.snapshot.find_all('img', src=self.url)
    
    def binary(self):
        with open(join(self.img_dir, 'image.webp'), 'rb') as f:
            return f.read()
    
    def __array__(self, dtype=None):
        try:
            image = iio.imread(join(self.img_dir, 'image.webp'))[:,:,:3]
        except:
            # transformers image_utils thinks dim < 4 are color channels and switches them around
            image = np.zeros((5, 5, 3), dtype=np.uint8)
            logger.warn(f'Could not read image in {self.img_dir}, using black image instead')
        return image
    
    def __repr__(self):
        return f'<Image {self.id}: {self.name}>'
    
    def __hash__(self):
        return self.id
    
    def __eq__(self, other):
        return hash(self) == hash(other)
    
class Page:
    
    def __init__(self, page_dir):
        self.page_dir = page_dir
        self.screenshot = join(self.page_dir, 'snapshot', 'screenshot.png')
        
    @property
    def url(self):
        with open(join(self.page_dir, 'page-url.txt'), 'r') as f:
            return f.read().rstrip()
        
    @property
    def xpath(self):
        with open(join(self.page_dir, 'snapshot', 'image-xpath.txt'), 'r') as f:
            return list(map(lambda x: x.rstrip(), f.readlines()))
        
    @property
    def snapshot(self):
        with open(join(self.page_dir, 'snapshot', 'dom.html'), 'r') as f:
            return f.read()
        
    def snapshot_parse(self):
        return BeautifulSoup(self.snapshot, 'html.parser')
        
    @property
    def snapshot_cleaned(self):
        with open(join(self.page_dir, 'snapshot', 'text.txt'), 'r') as f:
            return f.read()

    def nodes(self):
        with open(join(self.page_dir, 'snapshot', 'nodes.jsonl')) as f:
            for line in f.readlines():
                yield json.loads(line)

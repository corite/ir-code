import numpy as np
import torch
from tqdm import tqdm
from transformers import CLIPProcessor, CLIPModel, CLIPTokenizer
from sklearn.neighbors import BallTree
from pyterrier import Transformer
import pandas as pd
import pyterrier as pt
import logging

logger = logging.getLogger(__name__)

class PyTerrierImageIndex:
    
    def __init__(self, index_dir):
        self.index_dir = index_dir
        try:
            self.index = pt.IndexFactory.of(index_dir)
        except:
            self.index = None
        
    def build(self, corpus_iter, rebuild=False):
        if self.index is not None and not rebuild:
            return
        logger.info('Building PyTerrier index...')
        iter_indexer = pt.IterDictIndexer(self.index_dir, overwrite=rebuild, meta={'docno': 25, 'image_id': 10, 'text': 4096})
        self.index = iter_indexer.index(corpus_iter)
        
class ClipImageIndex:
    
    def __init__(self, index_file):
        self.index_file = index_file
        try:
            self.index = np.load(self.index_file)
        except OSError:
            self.index = None
    
    def build(self, images, rebuild=False):
        if self.index is not None and not rebuild:
            return
        self.index = np.empty((len(images), 512))
        with torch.no_grad():
            logger.info('Building CLIP index...')
            model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            for image in tqdm(images):
                inputs = processor(images=np.array(image), return_tensors="pt")
                image_features = model.get_image_features(**inputs)
                features = image_features.numpy()[0]
                features = features / np.linalg.norm(features)
                self.index[image.id] = features
        np.save(self.index_file, self.index)
                
class ClipImageSearch:
    
    def __init__(self, image_dataset, image_index):
        self.images = image_dataset
        self.tree = BallTree(image_index.index)
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-base-patch32")
        
    def text2vec(self, text):
        with torch.no_grad():
            inputs = self.tokenizer([text], padding=True, return_tensors="pt")
            text_features = self.model.get_text_features(**inputs)
            t_features = text_features.numpy()
            return t_features / np.linalg.norm(t_features)
        
    def query(self, query, results=50):
        dist, ind = self.tree.query(self.text2vec(query), k=results)
        res = [self.images[i] for i in ind[0]]
        for image, dist in zip(res, dist[0]):
            image.dist = dist
        return res
    
    def query_avg(self, queries, results=50):
        dist, ind = self.tree.query(np.mean([self.text2vec(q) for q in queries], axis=0), k=results)
        res = [self.images[i] for i in ind[0]]
        for image, dist in zip(res, dist[0]):
            image.dist = dist
        return res
    
class ClipRetrieve(Transformer):
    
    def __init__(self, clip_index, images, num_results):
        self.clip_search = ClipImageSearch(images, clip_index)
        self.num_results = num_results
        
    def transform(self, queries):
        retrieval_results = []
        for qid, query in zip(queries['qid'], queries['query']):
            img_res = self.clip_search.query(query, results=self.num_results)
            retrieval_results += [(qid, image.name, image.dist) for image in img_res]
        
        results = pd.DataFrame(retrieval_results, columns=['qid', 'docno', 'score'])
        results['rank'] = results.sort_values(by='score').groupby('qid').cumcount()
        
        return pd.merge(queries, results, on='qid')
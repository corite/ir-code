import numpy as np
import torch
from tqdm import tqdm
from transformers import CLIPProcessor, CLIPModel, CLIPTokenizer
from sklearn.neighbors import BallTree
from pyterrier import Transformer
import pandas as pd

class ClipImageIndex:
    
    def __init__(self, file=None):
        if file:
            self.load(file)
        else:
            self.index = None
    
    def save(self, file):
        np.save(file, self.index)
    
    def load(self, file):
        self.index = np.load(file)
    
    def build(self, images):
        self.index = np.empty((len(images), 512))
        with torch.no_grad():
            model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            for image in tqdm(images):
                inputs = processor(images=np.array(image), return_tensors="pt")
                image_features = model.get_image_features(**inputs)
                features = image_features.numpy()[0]
                features = features / np.linalg.norm(features)
                self.index[image.id] = features
                
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
        print('clip:')
        print(results)
        res = pd.merge(queries, results, on='qid')
        print(res)
        return res
import numpy as np
import torch
from tqdm import tqdm
from transformers import CLIPProcessor, CLIPModel, CLIPTokenizer
from sklearn.neighbors import BallTree

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
        
    def query(self, query, results=50):
        with torch.no_grad():
            inputs = self.tokenizer([query], padding=True, return_tensors="pt")
            text_features = self.model.get_text_features(**inputs)
            t_features = text_features.numpy()
            t_features = t_features / np.linalg.norm(t_features)
            dist, ind = self.tree.query(t_features, k=results)
            return [self.images[i] for i in ind[0]]
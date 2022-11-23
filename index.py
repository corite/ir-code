import numpy as np
import torch
from tqdm import tqdm
from transformers import CLIPProcessor, CLIPModel

class ClipImageIndex:
    
    def __init__(self):
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
                self.index[image.id] = features
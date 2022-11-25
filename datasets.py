import os
from os.path import join
from torch.utils.data import Dataset
import imageio.v3 as iio
from functools import cached_property

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
        if isinstance(idx, slice):
            return [self[i] for i in range(*idx.indices(len(self)))]
        else:
            image_id = self.image_ids[idx]
            return Image(idx, image_id, join(self.root_dir, image_id[:3], image_id))
    
class Image:
    
    def __init__(self, img_id, img_name, img_dir):
        self.id = img_id
        self.name = img_name
        self.img_dir = img_dir
        self.image = None
        
    @cached_property
    def url(self):
        with open(join(self.img_dir, 'image-url.txt'), 'r') as f:
            return f.read()
    
    def __array__(self, dtype=None):
        if not self.image:
             self.image = iio.imread(join(self.img_dir, 'image.webp'))[:,:,:3]
        return self.image
    
    def __repr__(self):
        return f'<Image {self.id}: {self.name}>'
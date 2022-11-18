import os
import numpy as np
from PIL import Image
from transformers import CLIPProcessor, CLIPModel


model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

picDirectory = '/Users/maxkoch/Documents/Studium/Information_Retrieval/images/all_Images'
valueArrPath = '/Users/maxkoch/Documents/Studium/Information_Retrieval/valueArr.npy'
indexArrPath = '/Users/maxkoch/Documents/Studium/Information_Retrieval/indexArr.npy'

valueArr = []
indexArr = []
index = 1

for file in os.listdir(picDirectory):
    picPath = (picDirectory + '/' + file)

    indexArr.append(file)

    image = Image.open(picPath)

    inputs = processor(images=image, return_tensors="pt")
    image_features = model.get_image_features(**inputs)

    valueArr.append(image_features.detach().numpy()[0])
    
    #progress
    print(index, "/ 23.842")
    index += 1

    image.close()


np.save(valueArrPath, valueArr)
np.save(indexArrPath, indexArr)




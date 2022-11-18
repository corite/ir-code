import numpy as np
from transformers import CLIPProcessor, CLIPModel, CLIPTokenizer
import os


def findBestPictures(numPicsToFind, textArr):
    #[id, dot product]
    #bestPics = [['0', 0] for i in range(numPicsToFind)]
    bestDotProducts = np.zeros(numPicsToFind)
    bestIndices = np.zeros(numPicsToFind)
    minDot = 0

    for i in range(numOfPics):
        dot = np.dot(valueArr[i], textArr)

        if minDot < dot:
            index = np.where(bestDotProducts == minDot)[0][0]

            bestDotProducts = np.delete(bestDotProducts, index)
            bestIndices = np.delete(bestIndices, index)
            bestDotProducts = np.append(bestDotProducts, dot)
            bestIndices = np.append(bestIndices, i)

            minDot = np.min(bestDotProducts)

    return bestIndices


valueArrPath = '/Users/maxkoch/Documents/Studium/Information_Retrieval/valueArr.npy'
indexArrPath = '/Users/maxkoch/Documents/Studium/Information_Retrieval/indexArr.npy'
picturesPath = '/Users/maxkoch/Documents/Studium/Information_Retrieval/images/all_Images/'

indexArr = np.load(indexArrPath)
valueArr = np.load(valueArrPath)

numOfPics = indexArr.size

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-base-patch32")

while True:
    query = input("Enter a query: ")

    inputs = tokenizer([query], padding=True, return_tensors="pt")
    text_features = model.get_text_features(**inputs)
    
    #get 1d array from tensor
    textArr = text_features.detach().numpy()[0]
    bestIndices = findBestPictures(5, textArr)

    shellCommand = ""

    for i in bestIndices:
        id = indexArr[int(i)]
        shellCommand += picturesPath + id + " "
    
    #shell open file command
    commandToOpenFile = "open"
    shellCommand = commandToOpenFile + " " + shellCommand
    os.system(shellCommand)
    




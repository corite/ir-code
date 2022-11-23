import matplotlib.pyplot as plt
import numpy as np

def image_grid(images):
    fig, axes = plt.subplots(nrows=len(images)//4 + 1, ncols=4, dpi=300)
    for index, ax in np.ndenumerate(axes):
        ax.axis('off')
    for (index, ax), im in zip(np.ndenumerate(axes), images):
        ax.imshow(im, origin="upper")
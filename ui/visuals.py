from IPython.display import display, HTML
from neville.ui import render_template

def image_results(images, hide=True):
    return display(HTML(render_template('image_results.html', images=images, hide=hide)))
from IPython.display import display, HTML
from neville.ui import render_template

def marked_text(sentences, probabilities):
    return display(HTML(render_template('marked_text.html', sentences=zip(sentences, map(lambda x: int(x*100), probabilities)))))
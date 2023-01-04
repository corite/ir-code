from IPython.display import display, HTML
from neville.ui import render_template

def image_results(image_results, hide=True):
    return display(HTML(render_template('image_results.html', image_results=image_results, hide=hide)))

def pro_con(pro, con, hide=True, doubles=False):
    if doubles:
        for image in pro:
            for i in con:
                if image.number == i.number:
                    image.is_double = True
        for image in con:
            for i in pro:
                if image.number == i.number:
                    image.is_double = True
    return display(HTML(render_template('two_col.html', pro=pro, con=con, hide=hide)))
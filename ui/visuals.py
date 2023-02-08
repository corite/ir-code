from IPython.display import display, HTML
from neville.ui import render_template

def image_results(image_results, hide=True):
    return display(HTML(render_template('image_results.html', image_results=image_results, hide=hide)))

def pt_results(images, pt_results):
    return image_results([images[image_id] for image_id in pt_results['docno']])

def pro_con(pro, con, hide=True, doubles=False):
    return two_col(pro, con, hide=hide, doubles=doubles)

def two_col(pro, con, ran=slice(None), labels=('pro', 'con'), hide=True, doubles=False):
    if doubles:
        for image in pro:
            for i in con:
                if image.id == i.id:
                    image.is_double = True
        for image in con:
            for i in pro:
                if image.id == i.id:
                    image.is_double = True
    return display(HTML(render_template('two_col.html', pro=pro[ran], con=con[ran], labels=labels, hide=hide)))
import jinja2
from PIL import Image
from io import BytesIO
import numpy as np
import base64
import os
from urllib.parse import urlparse

jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates/'))

def reencode_image(image):
    ''' slower but supports images not stored as webp on disk '''
    img = Image.fromarray(np.array(image))
    img.thumbnail((1000, 250))
    bytes_image = BytesIO()
    img.save(bytes_image, format='webp', quality=80, method=0)
    img_encoded = base64.b64encode(bytes_image.getvalue()).decode()
    return 'data:image/WEBP;base64,' + img_encoded

def encode_image(image):
    img_encoded = base64.b64encode(image.binary()).decode()
    return 'data:image/WEBP;base64,' + img_encoded

def get_domain(url):
    return urlparse(url).netloc

jinja_env.filters['encode'] = encode_image
jinja_env.filters['domain'] = get_domain

def render_template(file_name, **context):
    return jinja_env.get_template(file_name).render(context)
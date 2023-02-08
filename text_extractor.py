from urllib.parse import urlparse
import os.path
import nltk
from boilerpy3.extractors import ArticleExtractor, ArticleSentencesExtractor
from boilerpy3.parser import BoilerpipeHTMLParser
from boilerpy3.marker import AnotherBoilerPipeHTMLParser
from html.parser import HTMLParser
from bs4 import BeautifulSoup

import logging
logging.basicConfig(level=logging.ERROR)

class MyBoilerPipeHTMLParser(BoilerpipeHTMLParser):
    
    def handle_startendtag(self, tag, attrs):
        HTMLParser.handle_startendtag(self, tag, attrs)
        
AnotherBoilerPipeHTMLParser.__bases__ = (MyBoilerPipeHTMLParser,)

article_extractor = ArticleSentencesExtractor(raise_on_failure=False)
extractor = ArticleExtractor(raise_on_failure=False)

def extract_filename(url):
    return os.path.basename(urlparse(url).path)
                
def to_sentences(text):
    return filter(lambda sentence: len(sentence) > 30, nltk.sent_tokenize(' '.join(text.splitlines())))
                
def extract_page_content(snapshot):      
    article = article_extractor.get_doc(snapshot)
    yield from to_sentences(article.title.split('|')[0])
    yield from to_sentences(article.content)
    
def extract_starting_at_tags(tags):
    processed = set()
    to_process = set(tags)
    while to_process:
        to_process_next = []
        for tag in to_process:
            for el in tag.find_all(attrs={'x-boilerpipe-marker': True}):
                if el not in processed:
                    processed.add(el)
                    yield from to_sentences(str(el.string))
            if tag.parent:
                to_process_next.append(tag.parent)
        to_process = set(to_process_next)
                
def extract_content(image):
    snapshot = image.page.snapshot
    if not all(['HEAD' in xpath for xpath in image.page.xpath]):
        filename = extract_filename(image.url)
        marked_html = extractor.get_marked_html(snapshot)
        marked_soup = BeautifulSoup(marked_html, 'lxml')
        marked_occurences = marked_soup.find_all(lambda element: any(filename in attr for attr in element.attrs.values()))
        
        if len(marked_occurences) == 0:
            yield from extract_page_content(snapshot)
            return
        
        imgs = list(filter(lambda element: element.name == 'img', marked_occurences))
        if len(imgs) != 0:
            for img in imgs:
                if img.has_attr('alt'):
                    yield from to_sentences(img['alt'])
            marked_occurences = imgs
            
        yield from extract_starting_at_tags(marked_occurences)
    else:
        yield from extract_page_content(snapshot)
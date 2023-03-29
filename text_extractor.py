import nltk
from boilerpy3.extractors import DefaultExtractor
from boilerpy3.parser import BoilerpipeHTMLParser
from boilerpy3.marker import AnotherBoilerPipeHTMLParser, HTMLBoilerpipeMarker
from html.parser import HTMLParser
from bs4 import BeautifulSoup, Tag
from itertools import cycle, islice
import re

nltk.download('punkt')

import logging
logging.getLogger('boilerpy3').setLevel(level=logging.ERROR)

class MyBoilerPipeHTMLParser(BoilerpipeHTMLParser):
    
    def handle_startendtag(self, tag, attrs):
        HTMLParser.handle_startendtag(self, tag, attrs)
        
AnotherBoilerPipeHTMLParser.__bases__ = (MyBoilerPipeHTMLParser,)

class MyExtractor(DefaultExtractor):

    def get_marked_html(self, text):
        doc = self.get_doc(text)
        marker = HTMLBoilerpipeMarker(raise_on_failure=self.raise_on_failure)
        marker.TA_IGNORABLE_ELEMENTS = set()
        marker.VOID_ELEMENTS = set()
        return marker.process(doc, text)

extractor = MyExtractor(raise_on_failure=False)

def to_sentences(text):
    return filter(lambda sentence: len(sentence) > 20, nltk.sent_tokenize(' '.join(text.splitlines())))

def get_content(tag):
    return tag.get_text()
                
def walk_down_in_tag(tag):
    if type(tag) is not Tag:
        return
    if tag.has_attr('x-boilerpipe-marker'):
        yield tag
    else:
        for child in tag.children:
            yield from walk_down_in_tag(child)
        
def walk_up_starting_at_tag(tag):
    while type(tag) is not BeautifulSoup:
        yield from roundrobin(
            tag.find_previous_siblings(attrs={'x-boilerpipe-marker': True}),
            tag.find_next_siblings(attrs={'x-boilerpipe-marker': True}))
        tag = tag.parent
        
def get_marked_tags(tag):
    return tag.find_all(attrs={'x-boilerpipe-marker': True})
                
def extract_content(image):
    img_tags = list(find_image_tags(image))
    print('=====================================')
    for i in img_tags:
        print(get_xpath(i))
    print('=====================================')
    if img_tags:
        for img in img_tags:
            if img.has_attr('alt'):
                yield from to_sentences(img['alt'])
        # TODO: find main img tag
        start_tag = img_tags[0]
        for tag in walk_up_starting_at_tag(start_tag):
            for text in map(get_content, walk_down_in_tag(tag)):
                yield from to_sentences(text)
    else:
        yield from to_sentences(extractor.get_content(image.page.snapshot))
        
def get_marked_soup(image):
    snapshot = image.page.snapshot
    marked_html = extractor.get_marked_html(snapshot)
    marked_soup = BeautifulSoup(marked_html, 'lxml')
    return marked_soup

def find_image_tags(image):
    soup = get_marked_soup(image)
    for occurence in image.page.xpath:
        yield find_node(soup, occurence)
    
def get_xpath_node(node):
    length = len(list(node.find_previous_siblings(node.name))) + 1
    return f'{node.name.upper()}[{length}]'

def get_xpath(node):
    path = [get_xpath_node(node)]
    for parent in node.parents:
        if type(parent) is BeautifulSoup:
            break
        path.insert(0, get_xpath_node(parent))
    return '/' + '/'.join(path)

def find_node(soup, xpath):
    node = soup
    element_regex = r'(.+)\[(\d+)\]'
    try:
        for element in xpath.split('/')[1:]:
            matches = re.match(element_regex, element)
            element_name = matches.group(1).lower()
            if element_name == 'noscript' and not node.find_all(element_name, recursive=False, limit=int(matches.group(2))):
                continue
            while node.contents[0].name == 'source':
                node.contents[0].unwrap()
            node = node.find_all(element_name, recursive=False, limit=int(matches.group(2)))[-1]
    except Exception as e:
        return None
    return node


def roundrobin(*iterables):
    "roundrobin('ABC', 'D', 'EF') --> A D E B F C"
    # Recipe credited to George Sakkis
    pending = len(iterables)
    nexts = cycle(iter(it).__next__ for it in iterables)
    while pending:
        try:
            for next in nexts:
                yield next()
        except StopIteration:
            pending -= 1
            nexts = cycle(islice(nexts, pending))
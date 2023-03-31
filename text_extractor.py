import nltk
from boilerpy3.extractors import DefaultExtractor
from boilerpy3.parser import BoilerpipeHTMLParser
from boilerpy3.marker import AnotherBoilerPipeHTMLParser, HTMLBoilerpipeMarker
from html.parser import HTMLParser
from bs4 import BeautifulSoup, Tag, NavigableString
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

def get_marked_and_images_ordered(soup, image_xpaths):
    ordered_lists = []
    current_list = []
    for tag in soup.descendants:
        if type(tag) is NavigableString and tag.parent.has_attr('x-boilerpipe-marker'):
            current_list.append(tag.parent)
        if type(tag) is Tag and get_xpath(tag) in image_xpaths and current_list:
            # insert image
            current_list.append(tag)
            if not ordered_lists:
                # first picture found
                ordered_lists.append(list(reversed(current_list)))
            else:
                # between two pictures
                ordered_lists.append(current_list[:len(current_list)//2])
                ordered_lists.append(list(reversed(current_list[len(current_list)//2:])))
            current_list = []
    ordered_lists.append(current_list)
    yield from roundrobin(*ordered_lists)
        
def get_marked_tags(tag):
    return tag.find_all(attrs={'x-boilerpipe-marker': True})
                
def extract_content(image):
    for tag in get_marked_and_images_ordered(get_marked_soup(image), image.page.xpath):
        if tag.name == 'img' and tag.has_attr('alt'):
            yield from to_sentences(tag['alt'])
        if tag.string:
            yield from to_sentences(tag.string)
        
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
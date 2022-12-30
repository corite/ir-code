import mistletoe
from mistletoe.base_renderer import BaseRenderer
from mistletoe import Document

class ListExtractor(BaseRenderer):
        
    def extract(self, token):
        if token.__class__.__name__ == 'ListItem':
            yield self.render(token)
        elif hasattr(token, 'children'):
            for t in token.children:
                yield from self.extract(t)

    def render_line_break(self, token):
        return ''
    
def extract_markdown_list(doc):
    with ListExtractor() as extractor:
        d = Document(doc)
        yield from extractor.extract(d)
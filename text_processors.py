import mistletoe
from mistletoe.base_renderer import BaseRenderer
from mistletoe import Document

class ListExtractor(BaseRenderer):
    
    def __init__(self):
        super().__init__()
        self.render_map = {
            'RawText': self.render_raw_text,
            'LineBreak': self.render_line_break,
        }
        
    def extract(self, token):
        if token.__class__.__name__ == 'Paragraph':
            yield self.render_paragraph(token)
        elif token.__class__.__name__ in self.render_map:
            return self.render_map[token.__class__.__name__](token)
        else:
            for t in token.children:
                yield from self.extract(t)
     
    def render_line_break(self, token):
        return ''
    
def extract_markdown_list(doc):
    with ListExtractor() as extractor:
        d = Document(doc)
        yield from extractor.extract(d)
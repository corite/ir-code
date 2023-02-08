from functools import partial

class StanceDetector():
    
    def __init__(self, stance, images, content_extractor=lambda image: image.page.snapshot_cleaned.split('.')):
        if stance not in ['PRO', 'CON']:
            raise ValueError('Only PRO and CON are allowed stances')
        self.stance = stance
        self.images = images
        self.content_extractor = content_extractor
        
    def score(self, query: str, sentences: (str)) -> float:
        return 0
    
    def _rerank(self, doc_row):
        image = self.images[doc_row['docno']]
        content = self.content_extractor(image)
        return self.score(doc_row['query'], content)
    
    def rerank(self):
        return partial(StanceDetector._rerank, self)
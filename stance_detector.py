from functools import partial
import pandas as pd

class StanceDetector():
    
    def __init__(self, stance, images, content_extractor=lambda image: image.page.snapshot_cleaned.split('.')):
        if stance not in ['PRO', 'CON']:
            raise ValueError('Only PRO and CON are allowed stances')
        self.stance = stance
        self.images = images
        self.content_extractor = content_extractor
        
    def score(self, query_docno_sentences: ((str, str, str))) -> float:
        return 0
    
    def _rerank(self, doc_rows):
        query_sentences = ((query, image_id, sentence) for query, image_id in zip(doc_rows['query'], doc_rows['docno']) for sentence in self.content_extractor(self.images[image_id]))
        # important: make sure index of doc_rows is preserved, otherwise returned results can't be matched
        result = doc_rows.drop(columns=['score']).join(self.score(query_sentences), on=['query', 'docno'])
        # set documents with no content, therefore not in the left join (NaN), to score 0
        return result['score'].fillna(0)
    
    def rerank(self):
        return partial(StanceDetector._rerank, self)

import pandas as pd
import pyterrier as pt

class StanceDetector():
    
    def __init__(self, index, images):
        self.index = index
        self.images = images
        
    def score(self, stance_query_docno_text: ((str, str, str, str))) -> pd.DataFrame:
        pass
    
    def __call__(self, doc_rows):
        stance_query_docno_text = ((stance, query, docno, self.index.getMetaIndex().getItem('text', self.index.getMetaIndex().getDocument('docno', docno))) for stance, query, docno in zip(doc_rows['stance'], doc_rows['query'], doc_rows['docno']))
        # important: make sure index of doc_rows is preserved, otherwise returned results can't be matched
        result = doc_rows.drop(columns=['score'], errors='ignore').join(self.score(stance_query_docno_text), on=['stance', 'query', 'docno'])
        # set documents with no content, therefore not in the left join (NaN), to score 0
        return result['score'].fillna(0)
    
def apply_stance(stance):
    if stance not in ['PRO', 'CON']:
        raise ValueError('Stance can only be PRO or CON')
    return pt.apply.generic(lambda df: df.assign(stance=stance))
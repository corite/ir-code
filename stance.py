import pandas as pd
import pyterrier as pt
from pyterrier.apply_base import ApplyDocumentScoringTransformer

class StanceDetector(ApplyDocumentScoringTransformer):
    
    def __init__(self, index, images):
        super().__init__(self.transform_fn, batch_size=1000)
        self.index = index
        self.images = images
        
    def score(self, stance_query_docno_text: ((str, str, str, str))) -> pd.DataFrame:
        pass
    
    def transform_fn(self, doc_rows):
        stance_query_docno_text = ((stance, query, docno, self.index.getMetaIndex().getItem('text', self.index.getMetaIndex().getDocument('docno', docno))) for stance, query, docno in zip(doc_rows['stance'], doc_rows['query'], doc_rows['docno']))
        # important: make sure index of doc_rows is preserved, otherwise returned results can't be matched
        result = doc_rows.drop(columns=['score'], errors='ignore').join(self.score(stance_query_docno_text), on=['stance', 'query', 'docno'])
        # set documents with no content, therefore not in the left join (NaN), to score 0
        return result['score'].fillna(0)
    
def apply_stance(stance):
    if stance not in ['PRO', 'CON']:
        raise ValueError('Stance can only be PRO or CON')
    return pt.apply.generic(lambda df: df.assign(stance=stance))

def flip_stance():
    def flip_stance_rows(df):
        df['stance'] = df.apply(lambda row: 'PRO' if row['stance'] == 'CON' else 'CON', axis=1)
        return df
    return pt.apply.generic(flip_stance_rows)

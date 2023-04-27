from transformers import pipeline
from neville.stance import StanceDetector
import pandas as pd

class SentimentAnalysis(StanceDetector):
    def __init__(self, index, images):
        super().__init__(index, images)
        #without neutral sentiment
        #sentiment_pipeline = pipeline(model='sentiment-analysis')
        
        #with neutral sentiment
        self.sentiment_pipeline = pipeline(model='finiteautomata/bertweet-base-sentiment-analysis')
        
    def score(self, stance_query_docno_text: ((str, str, str, str))) -> pd.DataFrame:
        stance_query_docno_score = ((stance, query, docno, self.score_sentiment(text, stance)) for stance, query, docno, text in stance_query_docno_text)

        df = pd.DataFrame(stance_query_docno_score, columns=['stance', 'query', 'docno', 'score'])
        return df.set_index(['stance', 'query', 'docno'])
        '''
        if df.empty:
            return df.set_index(['stance', 'query', 'docno'])
        else:
            df['score'] = df['score'].where(df['stance'] == 'PRO', -df['score']) + 1
            return df.groupby(['stance', 'query', 'docno']).agg(self.aggfunc, numeric_only=True)
        '''
    
    def score_sentiment(self, text: str, stance: str):
        sentiment_score = self.sentiment_pipeline([text], truncation=True)[0]
        
        if (stance == 'PRO' or stance == 'pro' or stance == 'POS' or stance == 'pos') and (sentiment_score['label'] == 'POS' or sentiment_score['label'] == 'POSITIVE'):
            return sentiment_score['score']
        
        if (stance == 'CON' or stance == 'con' or stance == 'NEG' or stance == 'neg') and (sentiment_score['label'] == 'NEG' or sentiment_score['label'] == 'NEGATIVE'):
            return sentiment_score['score']
        
        return 0
    
    def rerank(self, results, stance):
        return sorted(results, key = lambda x: self.score_sentiment(x.page.snapshot_cleaned, stance))
    
    def rerank_fitting_sentiment_only(self, results, stance):
        new_res = []
        
        for result in results:
            score = self.score_sentiment(result.page.snapshot_cleaned, stance)
            if score > 0:
                new_res.append([result, score])
        
        new_res = sorted(new_res, key = lambda x: x[1])
        return [i[0] for i in new_res]
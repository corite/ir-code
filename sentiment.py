from transformers import pipeline

class SentimentAnalysis:
    def __init__(self):
        #without neutral sentiment
        #sentiment_pipeline = pipeline(model='sentiment-analysis')
        
        #with neutral sentiment
        self.sentiment_pipeline = pipeline(model='finiteautomata/bertweet-base-sentiment-analysis')
    
    def score_sentiment(self, text:str, stance:str):
        sentiment_score = self.sentiment_pipeline([text])[0]
        
        if (stance == 'PRO' or stance == 'pro' or stance == 'POS' or stance == 'pos') and sentiment_score['label'] == 'POS':
            return sentiment_score['score']
        
        if (stance == 'CON' or stance == 'con' or stance == 'NEG' or stance == 'neg') and sentiment_score['label'] == 'NEG':
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
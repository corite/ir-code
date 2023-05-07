from debater_python_api.api.debater_api import DebaterApi
from neville.stance import StanceDetector
import nltk
import pandas as pd
import savestate
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DebaterStanceDetector(StanceDetector):
    
    def __init__(self, index, images, api_token, aggfunc='mean', sentences=None, cache_file='/tmp/debater-cache-tmp'):
        super().__init__(index, images)
        self.api = DebaterApi(api_token)
        self.aggfunc = aggfunc
        self.sentences = sentences
        self.cache_file = cache_file

    def get_stances(self, stance_query_docno_sentences: [(str, str, str, str)]):
        '''computes the stance of each sentence in the range of [-1, 1]'''
        if len(stance_query_docno_sentences) == 0:
            return []
        pro_con_client = self.api.get_pro_con_client()
        pro_con_client.set_show_process(False)
        sentence_topic_dicts = [{'sentence': sentence, 'topic': query } for stance, query, docno, sentence in stance_query_docno_sentences]
        try:
            results = pro_con_client.run(sentence_topic_dicts)
            return results
        except ConnectionError:
            logger.error('Connection to debater failed, returning empty results')
            return []
    
    def score(self, stance_query_docno_text: ((str, str, str, str))) -> pd.DataFrame:
        stance_query_docno_sentences = ((stance, query, docno, sentence) for stance, query, docno, text in stance_query_docno_text for sentence in nltk.sent_tokenize(text)[:self.sentences])
        
        with savestate.open(Path(self.cache_file), 'c') as db:
            stance_query_docno_score = []
            non_cached_stance_query_docno_sentences = []
            for stance, query, docno, sentence in stance_query_docno_sentences:
                key = str((query, sentence))
                if key in db:
                    stance_query_docno_score.append((stance, query, docno, db[key]))
                else:
                    non_cached_stance_query_docno_sentences.append((stance, query, docno, sentence))
                    
            stances = self.get_stances(non_cached_stance_query_docno_sentences)
            
            for score, (stance, query, docno, sentence) in zip(stances, non_cached_stance_query_docno_sentences):
                db[str((query, sentence))] = score
                stance_query_docno_score.append((stance, query, docno, score))

            df = pd.DataFrame(stance_query_docno_score, columns=['stance', 'query', 'docno', 'score'])
            if df.empty:
                return df.set_index(['stance', 'query', 'docno'])
            else:
                df['score'] = df['score'].where(df['stance'] == 'PRO', -df['score']) + 1
                return df.groupby(['stance', 'query', 'docno']).agg(self.aggfunc, numeric_only=True)

from debater_python_api.api.debater_api import DebaterApi
from neville.stance_detector import StanceDetector
import pandas as pd
import shelve

class DebaterStanceDetector(StanceDetector):
    
    def __init__(self, stance, images, content_extractor, api_token, cache_file='/tmp/debater-cache.db'):
        super().__init__(stance, images, content_extractor)
        self.api = DebaterApi(api_token)
        self.cache_file = cache_file

    def get_stances(self, query_docno_sentences: [(str, str, str)]):
        '''computes the stance of each sentence in the range of [-1, 1]'''
        if len(query_docno_sentences) == 0:
            return []
        pro_con_client = self.api.get_pro_con_client()
        pro_con_client.set_show_process(False)
        sentence_topic_dicts = [{'sentence': sentence, 'topic': query } for query, docno, sentence in query_docno_sentences]
        return pro_con_client.run(sentence_topic_dicts)
    
    def score(self, query_docno_sentences: ((str, str, str))) -> [float]:
        with shelve.open(self.cache_file) as db:
            query_docno_values = []
            non_cached_query_docno_sentences = []
            for query, docno, sentence in query_docno_sentences:
                key = str((query, sentence))
                if key in db:
                    query_docno_values.append((query, docno, db[key]))
                else:
                    non_cached_query_docno_sentences.append((query, docno, sentence))
                    
            stances = self.get_stances(non_cached_query_docno_sentences)
            
            for value, (query, docno, sentence) in zip(stances, non_cached_query_docno_sentences):
                db[str((query, sentence))] = value
                query_docno_values.append((query, docno, value))

            df = pd.DataFrame(query_docno_values, columns=['query', 'docno', 'score'])
            df_grouped = df.groupby(['query', 'docno']).mean()
            if self.stance == 'CON':
                df_grouped['score'] *= -1
            df_grouped['score'] += 1
            return df_grouped
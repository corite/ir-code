from debater_python_api.api.debater_api import DebaterApi
from statistics import mean
from neville.stance_detector import StanceDetector

class DebaterStanceDetector(StanceDetector):
    
    def __init__(self, stance, images, content_extractor, api_token):
        super().__init__(stance, images, content_extractor)
        self.api = DebaterApi(api_token)

    def get_stances(self, sentences: [str], topic: str):
        '''computes the stance of each sentence in the range of [-1, 1]'''
        pro_con_client = self.api.get_pro_con_client()
        pro_con_client.set_show_process(False)
        sentence_topic_dicts = [{'sentence': sentence, 'topic': topic } for sentence in sentences]
        if len(sentence_topic_dicts) == 0:
            return []
        return pro_con_client.run(sentence_topic_dicts)
    
    def score(self, query: str, sentences: (str)) -> float:
        stances = self.get_stances(sentences, query)
        
        if len(stances) != 0:
            avg = mean(stances)
            if self.stance == 'CON':
                return -avg + 1
            else:
                return avg + 1
        else:
            return 0
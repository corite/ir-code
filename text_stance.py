from debater_python_api.api.debater_api import DebaterApi
from statistics import mean

class TextProcessor:
    def __init__(self, token):
        self.api = DebaterApi(token)
    
    def clean(self, text:str): #does some "dumb" cleanup. The goal is to get the main website text without website navigation elements, ads etc
        lines = []
        for line in text.split("\n"):
            if len(line.strip().split()) > 10 and not "cookie" in line.lower(): # clean blank lines and website elements which are not the main text
                lines.append(line.strip())
        return list(filter(lambda s: s != "", ".".join(lines).split("."))) # returns a list of "sentences".   

    def filter_relevant(self, sentences:[str],topic:str): # tries to filter out off-topic sentences using the debater api 
        if len(sentences) == 0:
            return []
        evidence_detection_client = self.api.get_evidence_detection_client()
        sentence_topic_dicts = [{'sentence':sentence, 'topic':topic} for sentence in sentences]
        scores = evidence_detection_client.run(sentence_topic_dicts)
        relevant_sentences = []
        for i in range(len(sentence_topic_dicts)):
            if scores[i] > 0.01: #we consider this relevant
                relevant_sentences.append(sentences[i])
        return relevant_sentences

    def get_key_points(self, sentences:[str]): # extract the key-points of a collectio of on-topic sentences
        if len(sentences) == 0:
            return []
        keypoints_client = self.api.get_keypoints_client()
        return keypoints_client.run(sentences)

    def get_stances(self, sentences:[str], topic:str): # computes the stance of each sentence in the range of -1 : 1
        if len(sentences) == 0:
            return []
        pro_con_client = self.api.get_pro_con_client()
        sentence_topic_dicts = [{'sentence' : sentence, 'topic' : topic } for sentence in sentences]
        return pro_con_client.run(sentence_topic_dicts)

    def get_stance_raw_txt(self, text:str, topic:str): # returns a value between 1 (PRO) and -1 (CON)
        sentences = self.clean(text)
        #raise Exception(sentences)
        relevant_sentences = self.filter_relevant(sentences, topic)
        #key_points = get_key_points(relevant_sentences)
        stances = self.get_stances(relevant_sentences, topic)
        #text_value = mean(stances)
        if len(stances) != 0:
            return max(stances)
        else:
            return 0

    def rerank(self, results, query, stance):
        return sorted(results, key = lambda x: self.get_stance_raw_txt(x.page.snapshot_cleaned, query), reverse = stance=="CON")
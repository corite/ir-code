import requests
from dataclasses import dataclass
from functools import cached_property

class ArgsMe:
    
    @staticmethod
    def query(query, num=10):
        headers = {'Accept': 'application/json'}
        params = {
            'query': query,
            'pageSize': num
        }
        res = requests.get('https://args.me/api/v2/arguments', params=params, headers=headers).json()
        return res
    
    @staticmethod
    def arguments(query, num=10):
        headers = {'Accept': 'application/json'}
        params = {
            'query': query,
            'fields': 'arguments.premises',
            'pageSize': num
        }
        res = requests.get('https://args.me/api/v2/arguments', params=params, headers=headers).json()
        arguments = []
        for arg in res['arguments']:
            for prem in arg['premises']:
                arguments.append(Argument(
                    text=prem['text'],
                    is_pro=prem['stance'] == 'PRO'))
        return ArgumentList(arguments)
    
class Summetix:
    
    @staticmethod
    def query(query, source='springer-x', num=10):
        headers = {'Accept': 'application/json'}
        request_body = {'topic': query, 'predictStance': True, 'computeAttention': True, 'numDocs': num, 'sortBy': 'argumentConfidence', 'beginDate': '', 'endDate': '', 'index': source}
        res = requests.post('https://ulb-da.summetix.com/search', headers=headers, json=request_body).json()
        return res
    
    @staticmethod
    def arguments(query, source='springer-x', num=10):
        headers = {'Accept': 'application/json'}
        request_body = {'topic': query, 'predictStance': True, 'computeAttention': False, 'numDocs': num, 'sortBy': 'argumentConfidence', 'beginDate': '', 'endDate': '', 'index': source}
        res = requests.post('https://ulb-da.summetix.com/search', headers=headers, json=request_body).json()
        arguments = []
        for arg in res['sentences']:
            arguments.append(Argument(
                text=arg['text'],
                is_pro=arg['stanceLabel'] == 'pro'))
        return ArgumentList(arguments)
    
@dataclass
class Argument:
    text: str
    is_pro: bool
                    
    @cached_property
    def is_con(self):
        return not self.is_pro

class ArgumentList(list):
    
    def pros(self):
        return filter(lambda arg: arg.is_pro, self)
    
    def cons(self):
        return filter(lambda arg: arg.is_con, self)
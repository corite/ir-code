import requests
import json
import re
import urllib.parse
from bs4 import BeautifulSoup
from dataclasses import dataclass

@dataclass
class SearchImage:
    image_url: str
    thumbnail_url: str
    page_url: str
    rank: int

class GoogleImageSearch:
    
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Host': 'www.startpage.com',
        'Origin': 'https://www.startpage.com',
        'Referer': 'https://www.startpage.com/',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0'
    }
    
    def __init__(self, session=None):
        if not session:
            self.req = requests.Session()
        else:
            self.req = session
        self.fresh_sc()
        
    def fresh_sc(self):
        resp = self.req.get('https://www.startpage.com/', headers=self.headers)
        soup = BeautifulSoup(resp.text, 'html.parser')
        self.sc = soup.find('input', {'name': 'sc'})['value']
        
    def search(self, query, pages=1):
        def extract_json(soup):
            app_js_reg = re.compile(r'(?<=UIStartpage.AppSerp, ){\"render.*}(?=\))')
            app_js_text = soup.find('script', string=app_js_reg).text
            app_json = app_js_reg.search(app_js_text).group()
            return json.loads(app_json)['render']['presenter']['regions']['mainline'][0]['results']
        
        def get_url(result):
            arguments = result['clickUrl'].split('?')[1]
            return urllib.parse.parse_qs(arguments)['piurl'][0]
        
        def results_from_page(page):
            data = {
                'lui': 'english',
                'language': 'english',
                'query': query,
                'cat': 'images',
                'sc': self.sc,
                't': '',
                'page': page
            }

            resp = self.req.post('https://www.startpage.com/sp/search', data=data, headers=self.headers)
            soup = BeautifulSoup(resp.text, 'html.parser')

            results = extract_json(soup)
            for result in results:
                yield SearchImage(image_url=get_url(result), page_url=result['displayUrl'], thumbnail_url=result['thumbnailUrl'], rank=result['sourceIndex'] + len(results)*(page-1))
                
        for page in range(1, pages + 1):
            yield from results_from_page(page)

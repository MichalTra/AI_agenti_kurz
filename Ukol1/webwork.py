import requests
import time
from bs4 import BeautifulSoup

            
retry_time = 10
default_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}


def get_page(url, headers=default_headers, retry_time=retry_time, **kwargs):
    """Load page code"""
    try:
        page = requests.get(url, headers=headers, **kwargs)
        if page.status_code != 200:
            print(f'Page {url} failed to load - status {page.status_code}')
            raise Exception()
    except Exception:
        print(f'Unable to load page {url} - will try again in {retry_time} seconds')
        time.sleep(retry_time)
        page = requests.get(url, headers=headers, **kwargs)
        if page.status_code != 200:
            raise Exception(f'Error! Unable to load page {url}'.format(url))
    
    return page


def get_parsed_page(url, headers=default_headers, retry_time=1, parser='lxml', **kwargs):
    page = get_page(url=url, headers=headers, retry_time=retry_time, **kwargs)
    parsed_page = BeautifulSoup(page.content, parser)
    return parsed_page, page


def extract_seznam_titles() -> list[str]:
    
    parsed_page, page = get_parsed_page(url='https://www.seznam.cz')
    
    titles = []
    
    h3s = parsed_page.findAll('h3')
    
    for h3 in h3s:
        a = h3.find('a')
        if (a is not None) and (a.has_attr('class')) and ('article__title' in a.get_attribute_list('class')):
            titles.append(a.text)
            
    return titles
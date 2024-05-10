import requests
from bs4 import BeautifulSoup

def get_text_from_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.get_text()

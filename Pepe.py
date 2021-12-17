from bs4 import BeautifulSoup
import requests
from random import choice

class Pepe:
    def __init__(self):
        pepe_url = 'https://rare-pepe.com/'

        pepe_html = requests.get(pepe_url).content

        soup = BeautifulSoup(pepe_html, 'html.parser')
        img_tag = soup.find_all('img', class_='attachment-thumbnail size-thumbnail')
        self.pepe_imgs = [img['src'] for img in img_tag]
    
    def get_pepe(self):
        return choice(self.pepe_imgs)
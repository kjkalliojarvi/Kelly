# -*- coding: UTF-8 -*-
__author__ = 'kari'

import requests
from bs4 import BeautifulSoup
import datetime

cards = requests.get('https://www.fintoto.fi/xml/cards.xml')
soup = BeautifulSoup(cards.text,'xml')
pvm = datetime.datetime.now().strftime('%d.%m.%Y')

for ravit in soup.find_all('card'):
    if ravit['date'] == pvm:
        a = ravit.find('pool')['file'].split('_')
        #b = a['file'].split('_')
        print ravit['name'], ravit['code'], ravit['track-code'], a[0]

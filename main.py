#divers tests...

import requests
from bs4 import BeautifulSoup
page = requests.get('https://brightdata.com/blog/how-tos/web-scraping-with-python#need')
print(page)
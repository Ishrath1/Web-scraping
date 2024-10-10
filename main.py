from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import openpyxl

excel = openpyxl.Workbook()
sheet = excel.active
sheet.title="Egalité"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://catalogue.univ-reunion.fr/primo-explore/search?query=any,contains,%C3%A9galit%C3%A9&tab=default_tab&search_scope=LSS_TOUT&vid=URN&offset=0')
    contenu = page.content() 
    soup = BeautifulSoup(contenu, 'lxml')
    print(soup.prettify())







    browser.close()

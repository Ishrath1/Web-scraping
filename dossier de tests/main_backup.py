"""
Réalisation d'un web scraper qui permettra de répertorier tous les ouvrages de l'université de La Réunion
qui comporte le mot "égalité"
"""


from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import openpyxl

excel = openpyxl.Workbook()
sheet = excel.active
sheet.title="Egalité"


# /!\ Les fonctions sont à peaufiner, elles sont assez brouillant

#Fonction qui va récupérer le contenu html qui nous intéresse
def get_content(url):
    with sync_playwright() as p:
        #créer une instance
        browser = p.chromium.launch(headless=True)

        #créer un contexte
        context = browser.new_context(viewport={"width":1920,'height':1080})
        page = context.new_page()

        page.goto('https://catalogue.univ-reunion.fr/primo-explore/search?query=any,contains,%C3%A9galit%C3%A9&tab=default_tab&search_scope=LSS_TOUT&vid=URN&offset=0')
        page.wait_for_selector("div[id=searchResultsContainer]")
        page.wait_for_selector('span[data-field-selector="creator"]:not(:empty)')
        
        # On récupère les données des créateurs qui sont générées par une requête JS => on n'y a pas accès
        # dans le code de la page
        creator_data = page.evaluate('''() => {
            return [...document.querySelectorAll('span[data-field-selector="creator"]')].map(span => span.innerText);
        }''')

        # TODO pour le lieu...
        place_data = ""

        # TODO pour la date car tous les items n'ont pas forcément une date et cela risque de perturber les associations diverses
        year_data = page.evaluate('''() => {
            return [...document.querySelectorAll('span[data-field-selector="creationdate"]')].map(span => span.innerText);
        }''')
        

        soup = BeautifulSoup(page.content(), 'lxml')
        browser.close()

        return [soup, creator_data, year_data]
    
#Fonction qui va extraire les différentes valeurs dont on a besoin 
def extract_content():
    soup = get_content("a")[0]
    createurs = get_content("a")[1]
    data = []

    # On va mettre les éléments dans une liste de dictionnaires...
    # Ici on fait ca juste pour être sur que tous se passe correctement
    # /!\ A terme, ces informations doivent être classées dans un fichier xlsx /!\
    
    for item in soup.select(".list-item-wrapper"):
        data.append({
            'Titre': item.select_one("h3").text,
            'Auteur/Réalisateur': item.select_one('span', attrs={'data-field-selector': 'creator'}).text,
            'Accessibilité': "Accessible en ligne" if item.select_one(".availability-status").text=="Accès en ligne" else "Sur place",
            'Année': "...",
            'Type de média' :item.select_one(".media-content-type").text,
            'Localisation': "...",
        })

    # Ici pas de soucis... On a exactement le bon nombre de créateurs alors on peut les rajouter directement dans l'ordre
    for i in range(len(data)):
        data[i]["Auteur/Réalisateur"] = createurs[i]
    
    print(data)

extract_content()
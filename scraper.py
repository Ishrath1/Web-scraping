"""
Réalisation d'un web scraper qui permettra de répertorier tous les ouvrages de l'université de La Réunion
qui comporte le mot "égalité"
"""

# Import divers 
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import openpyxl
import re


# Préparation du fichier .xslx
excel = openpyxl.Workbook()
sheet = excel.active
sheet.title="Médias sur l'égalité"
sheet.append(["Type de média","Titre","Auteur/Réalisateur","Année","Accessibilité"])

#Fonction qui va récupérer le contenu html qui nous intéresse
def get_content(offset):
    with sync_playwright() as p:
        #créer une instance
        browser = p.chromium.launch(headless=True)

        #créer un contexte
        context = browser.new_context(viewport={"width":1920,'height':1080})
        page = context.new_page()

        url = f'https://catalogue.univ-reunion.fr/primo-explore/search?query=any,contains,%C3%A9galit%C3%A9&tab=default_tab&search_scope=LSS_TOUT&vid=URN&offset={offset}'
        page.goto(url)
        
        #Plusieurs wait pour être sûr que la page a le temps de charger tous le contenu qu'on recherche
        page.wait_for_selector("div[id=searchResultsContainer]")
        page.wait_for_selector("div[class=list-item-wrapper]")
        page.wait_for_selector(".result-item-details")
        page.wait_for_selector(".media-content-type")
        page.wait_for_selector(".availability-status")
        
        print("page", offset, "chargée")
        
        soup = BeautifulSoup(page.content(), 'lxml')

        # bloc servant à repérer s'il y a une page suivante mais ce n'était pas fonctionnel
        # à améliorer éventuellement...
        """if page.locator('button[aria-label="Charger plus de résultat"]'):
            print("selecteur")
            new_offset = offset + 10
        else:
            print("pas de selecteur :()")
            new_offset = 0"""

        browser.close()
        print("Ok pour récupérer le html de la page", offset)
        return(soup)
    

# Fonction pour extraire l'année d'une chaine de caractère...
def recup_annee(ch):
    res = re.findall(r"\b\d{4}\b",ch)

    #nettoyer les valeurs qui sont supérieures à une année choisie arbitrairement
    if len(res)>0:
        for e in res:
            if int(e) > 2026:
                res.remove(e)

    return(res)


#Fonction qui va extraire les différentes valeurs dont on a besoin 
def extract_content(offset):
    # Initialisation d'une liste pour récupérer les données nécessaires
    data = []

    # On récupère notre élément soup
    soup=get_content(offset)

    # On va mettre les éléments dans une liste de dictionnaires...
    # On met toujours une valeur par défaut dans le cas où la donnée n'existe pas
    for item in soup.select(".result-item-text"):
        data.append({
            'Titre': item.select_one("h3").text if item.select_one("h3").text else "N/A" ,
            'Auteur/Réalisateur': item.select_one("span[data-field-selector= 'creator']").text if item.select_one("span[data-field-selector= 'creator']") else "N/A",
            'Accessibilité': "Accessible en ligne" if item.select_one(".availability-status").text=="Accès en ligne" else "Sur place",
            'Année': item.select_one("span[data-field-selector='creationdate']").text if item.select_one("span[data-field-selector='creationdate']")
                else item.select_one("span[data-field-selector='isPartOf']").text if item.select_one("span[data-field-selector='isPartOf']") else "N/A",
            'Type de média' :item.select_one(".media-content-type").text if item.select_one(".media-content-type").text else "N/A",
            #'Localisation': "...", pas pour le moment
        })


    # Pour l'année, il y a parfois plus d'informations que necessaire, on va donc vérifier que l'on a bien que des années
    for j in range(len(data)):
        if len(data[j]["Année"]) > 4:
            data[j]["Année"] = recup_annee(data[j]["Année"])[0]

    # On va maintenant mettre ces données dans notre fichier xlsx (cela aurait pu se faire en même temps que l'étape precedente...)
    for i in range(len(data)):
        sheet.append([data[i]["Type de média"], data[i]["Titre"], data[i]["Auteur/Réalisateur"],data[i]["Année"],data[i]["Accessibilité"]])
    

# Fonction qui va récupérer le contenu sur toutes les pages
def scraper():
    # On change l'offset pour passer à la page suivante
    # Fonction qui pourrait être améliorée
    for offset in range(0,2000,10):
        print("page",offset, "en cours")
        extract_content(offset)
        print("page", offset, "finie")

    excel.save("fichier_egalite.xlsx")
    print("ok fini")

scraper()

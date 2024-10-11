"""
Réalisation d'un web scraper qui permettra de répertorier tous les ouvrages de l'université de La Réunion
qui comporte le mot "égalité"
"""


"""
TODO fini...
1) Améliorer le code des fonctions
2) Automatiser le processus sur l'ensemble des pages
3) Transférer les données dans un tableau Excel

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

# /!\ Les fonctions sont à peaufiner, elles sont assez brouillant

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
        page.wait_for_selector('span[data-field-selector="creator"]:not(:empty)')
        page.wait_for_selector(".media-content-type")
        page.wait_for_selector(".availability-status")
        
        print("page", offset, "chargée")


        #******#
        # Apparemment ça fonctionne sans ces éléments mais je les garde dans l'eventualité où ça ne marcherait plus 

        # On récupère les données des créateurs qui sont générées par une requête JS => on n'y a pas accès
        # dans le code de la page
        #creator_data = page.evaluate('''() => {
           # return [...document.querySelectorAll('span[data-field-selector="creator"]')].map(span => span.innerText);
        #}''')

        # Idem pour la date

        #year_data = page.evaluate('''() => {
            #return [...document.querySelectorAll('span[data-field-selector="creationdate"], span[data-field-selector="isPartOf"]')].map(span => span.innerText);
        #}''')

        #******#

        
        soup = BeautifulSoup(page.content(), 'lxml')

        if page.locator('button[aria-label="Charger plus de résultat"]'):
            print("selecteur")
            new_offset = offset + 10
        else:
            print("pas de selecteur :()")
            new_offset = 0

        browser.close()
        print("Ok pour récupérer le html de la page", offset)

        #return(soup, creator_data, year_data, new_offset)
        return(soup,new_offset)
    

#fonction pour extraire l'année d'une chaine de caractère...
def recup_annee(ch):
    res = re.findall(r"\b\d{4}\b",ch)

    #nettoyer les valeurs qui supérieure à une année choisie arbitrairement
    if len(res)>0:
        for e in res:
            if int(e) > 2026:
                res.remove(e)

    return(res)


#Fonction qui va extraire les différentes valeurs dont on a besoin 
def extract_content(offset):
    data = []
    #soup, creator_data, year_data, new_offset = get_content(offset)
    soup, new_offset=get_content(offset)


    #******#
    #nettoyer les valeurs années...
    #for y in range(len(year_data)):
        #if len(year_data[y]) > 4:
            #year_data[y] = recup_annee(year_data[y])[0]
    #******#



    # On va mettre les éléments dans une liste de dictionnaires...
    # Ici on fait ca juste pour être sur que tous se passe correctement
    # /!\ A terme, ces informations doivent être classées dans un fichier xlsx /!\
    
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


    # Pour nettoyer les valeurs de année
    for j in range(len(data)):
        if len(data[j]["Année"]) > 4:
            data[j]["Année"] = recup_annee(data[j]["Année"])[0]
        print(data[j], end="\n")

    
    
    #******#
    """for x in range(len(data)):
        for auteur in data[x]["Auteur/Réalisateur"]:
            if auteur == "N/A":
                print("un element de auteur manque")
                creator_data.insert(x, "N/A")
                print("ok on l'a rajouté")"""
    #******#


    for i in range(len(data)):
        #data[i]["Auteur/Réalisateur"] = creator_data[i]
        #data[i]["Année"] = year_data[i]
        sheet.append([data[i]["Type de média"], data[i]["Titre"], data[i]["Auteur/Réalisateur"],data[i]["Année"],data[i]["Accessibilité"]])
    

    return(new_offset)




"""def scraper():
    print("ok")
    with sync_playwright() as p:
        print("ok")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("ok")
        offset = 0
        plus_de_pages = True
        
        while plus_de_pages:
            extract_content(offset)
            print("ok pour ajouter les données de la page",offset)

            suivant = page.query_selector('button[aria-label="Charger plus de résultat"]')

            if suivant:
                offset += 10
            else:
                plus_de_pages = False

        browser.close()
        excel.save("egalite.xlsx")
        print("ok tout fini")"""


def scraper():

    new_offset = extract_content(0)
    print("ok page 0 ajoutée")
    
    
    while True:
        print("ok page", new_offset, "en cours")
        new_offset = extract_content(new_offset)
        print("ok page en question finie")

        if new_offset:
            continue
        else:
            break

    excel.save("fichier_egalite.xlsx")
    print("ok fini")



scraper()
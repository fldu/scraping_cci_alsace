from bs4 import BeautifulSoup
import pandas as pd
import requests
import lxml
from random import randint
from time import sleep

header = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2"}
iterator = 0
df = pd.DataFrame(columns=["Company name", "Company APE", "APE detail", "Company street", "Company ZIP", "Company city", 'Company mail', 'Company contact', 'Company size', 'Company Phone', "CA", "Company CCI link"])
r = requests.get("https://www.alsace-eurometropole.cci.fr/annuaire/annuaire-des-entreprises-alsace?page=0", headers=header)

while "Votre recherche n’a donné aucun résultat" not in r.text and r.status_code == 200:
    print(f"Iteration: {iterator}")
    url = f"https://www.alsace-eurometropole.cci.fr/annuaire/annuaire-des-entreprises-alsace?page={iterator}"
    r = requests.get(url, headers=header)
    soup = BeautifulSoup(r.text, 'lxml')
    for x in range(1,10):
        company_street = ""
        company_mail = ""
        company_contact = ""
        company_size = ""
        company_phone = ""
        comapny_CA = ""
        data = soup.find_all('div', {'class': f'views-row-{x}'})[0]
        data_link = data.a.get('href').split('\n')[0]
        data_text = data.get_text().split('\n')
        try:
            company_name = data_text[1]
        except:
            company_name = "Error"
        try:
            company_link = f"https://www.alsace-eurometropole.cci.fr{data_link}"
        except:
            company_link = "Error"
        try:
            company_city = data_text[3].split(':  ')[1].split(' - ')[0]
        except:
            company_link = "Error"
        try:
            zip_code = data_text[3].split(':  ')[1].split(' - ')[1]
        except:
            zip_code = "Error"
        try:
            company_ape = data_text[5]
        except:
            company_ape = "Error"
        try:
            ape_detail = data_text[7]
        except:
            ape_detail = "Error"

        if company_link != "Error":
            r_company = requests.get(company_link, headers=header)
            soup_company = BeautifulSoup(r_company.text, 'lxml')
            try:
                company_street = soup_company.find('div', {'class':'thoroughfare'}).get_text()
            except:
                company_street = "No info"
            try:
                company_mail = soup_company.find('div', {'class':'field-name-field-aa-email'}).find('div', {'class': 'field-item even'}).get_text()
            except:
                company_mail = "Non"
            if company_mail == "Non":
                company_mail = "No info"
            try:
                company_contact = soup_company.find_all('div', {'class':'field-name-field-aa-ape'})[1].find('div', {'class': 'field-item even'}).get_text()
            except:
                company_contact = "No info"
            try:
                company_size = soup_company.find('div', {'class':'field-name-field-aa-effectif'}).find('div', {'class': 'field-item even'}).get_text()
            except:
                company_size = "No info"
            try:
                company_phone = soup_company.find('div', {'class':'field-name-field-aa-telephone'}).find('div', {'class': 'field-item even'}).get_text()
            except:
                company_phone = "No info"
            try:
                company_CA = soup_company.find('div', {'class':'ca'}).find('div', {'class': 'field-items'}).get_text().replace('\n','')
            except:
                company_CA = "No info"

        df = df.append(pd.Series([company_name, company_ape, ape_detail, company_street, zip_code, company_city, company_mail, company_contact, company_size, company_phone, comapny_CA, company_link], index=df.columns), ignore_index=True)
        
    #sleep(randint(0,3)) # I said I'm a real user!
    return_code = r.status_code
    iterator += 1

df.to_excel('./output/output.xlsx', index=False)
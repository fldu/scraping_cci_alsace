from bs4 import BeautifulSoup
import pandas as pd
import requests
import lxml
from random import randint
from time import sleep
from celery import Celery
import celery
from os.path import join, dirname
from os import getenv
from dotenv import load_dotenv
from sqlalchemy import create_engine

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

db_name = getenv('MYSQL_DATABASE')
db_user = getenv('MYSQL_USER')
db_password = getenv('MYSQL_PASSWORD')

app = Celery('cci', broker="amqp://broker//", backend="rpc://logging//")
db_connector = create_engine(f"mysql+mysqlconnector://{db_user}:{db_password}@db/{db_name}")


@app.task
def get_company(iterator):
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2"}
    url = f"https://www.alsace-eurometropole.cci.fr/annuaire/annuaire-des-entreprises-alsace?page={iterator}"
    r = requests.get(url, headers=header)
    soup = BeautifulSoup(r.text, 'lxml')
    if "Votre recherche n’a donné aucun résultat" in r.text:
        return False
    for x in range(1,10):
        try:
            company_street = ""
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
            df_to_sql = pd.DataFrame(columns=["Company name", "Company APE", "APE detail", "Company street", "Company ZIP", "Company city", 'Company contact', 'Company size', 'Company Phone', "CA", "Company CCI link"])
            df_to_sql = df_to_sql.append(pd.Series([company_name, company_ape, ape_detail, company_street, zip_code, company_city, company_contact, company_size, company_phone, comapny_CA, company_link], index=df_to_sql.columns), ignore_index=True)
            df.to_sql(con=db_connector, name="output", if_exists="append", index=False)
        except Exception as e:
            print(f"error in code: {e}")
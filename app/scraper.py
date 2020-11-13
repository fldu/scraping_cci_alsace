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
from tasks import get_company

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

db_name = getenv('MYSQL_DATABASE')
db_user = getenv('MYSQL_USER')
db_password = getenv('MYSQL_PASSWORD')

app = Celery('cci', broker="amqp://broker//", backend="rpc://broker//")
db_connector = create_engine(f"mysql+mysqlconnector://{db_user}:{db_password}@db/{db_name}")

queue = []
   

def queue_check():
    for message in queue:
        if message.state != "PENDING":
            queue.remove(message)

##Main Code here
def main():
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2"}

    for i in range(0,8120):
        x = get_company.delay(i)
        queue.append(x)
        print(i)

    while len(queue) > 0:
        queue_check()
        sleep(10)
        print("Waiting 10s to empty queue")

    df = pd.read_sql(f"SELECT * FROM output", con=db_connector)
    df.to_excel('./output/output.xlsx', index=False)

main()
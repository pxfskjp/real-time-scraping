import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from lxml import etree

'/html/body/div[1]/div/main/div[2]'
scraped_url = 'https://tokenfomo.io/'
dislpayed_url = 'https://the-great-token-filter.com/'

header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
}

with requests.session() as s:
    tokenfomo = s.get(scraped_url, headers=header)

    soup = BeautifulSoup(tokenfomo.content, 'html.parser')
    table_data = soup.find('table')
    browser = webdriver.Chrome(ChromeDriverManager().install())
    browser.get(dislpayed_url)
    displayed_tag = browser.find_element_by_id('body')
    script = "arguments[0].insertAdjacentHTML('afterEnd', arguments[1])"
    browser.execute_script(script, displayed_tag, str(table_data))

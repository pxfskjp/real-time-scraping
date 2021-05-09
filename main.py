import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import mysql.connector
from time import sleep

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="blacvdls_tokendb"
)

mycursor = mydb.cursor(buffered=True)
'/html/body/div[1]/div/main/div[2]'
url = 'https://tokenfomo.io/'
header = {
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
}

browser = webdriver.Chrome(ChromeDriverManager().install())
browser.get(url)
# browser.find_element_by_tag_name('tfoot').click()
# sleep(3)
data = browser.find_elements_by_tag_name('tr')
for index, row in enumerate(data) :
  if index == (len(data)-1) :
    break
  home_name = row.find_elements_by_tag_name('td')[0].text
  home_symbol = row.find_elements_by_tag_name('td')[1].text
  contract = row.find_elements_by_tag_name('td')[2].find_element_by_tag_name('span').find_element_by_tag_name('span').text
  bscscan_url = row.find_elements_by_tag_name('td')[3].find_element_by_tag_name('a').get_attribute('href')
  with requests.session() as s:
    bscscan = s.get(bscscan_url, headers=header)
    soup = BeautifulSoup(bscscan.content, 'html.parser')
    contract_number = soup.find(class_='clipboard-hover').get_text()
  bscscan = row.find_elements_by_tag_name('td')[3].find_element_by_tag_name('span').text
  pancakeswap = row.find_elements_by_tag_name('td')[4].find_element_by_tag_name('span').text
  time = row.find_elements_by_tag_name('td')[5].text
  print(home_name, home_symbol, mono, bscscan, pancakeswap, time)
# print(data)
browser.quit()
            # id_sql = "select id from pages_teams where name = '%s'" % (team_name)
            # exist_id = mycursor.execute(id_sql)
            # exist_ids = mycursor.fetchone()
            # if exist_ids==None:
            #     sql = "insert into pages_teams (name) values ('%s')" % (team_name)
            #     mycursor.execute(sql)
            #     mydb.commit()
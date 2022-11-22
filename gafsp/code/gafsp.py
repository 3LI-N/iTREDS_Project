import requests
from bs4 import BeautifulSoup
import re
from urllib.request import unquote

url = 'https://www.gafspfund.org/projects/west-africa-food-system-resilience-program-fsrp'
response = requests.get(url)
content = BeautifulSoup(response.text, 'lxml')

pdf_urls = content.find_all('a')

for url in pdf_urls:
  try:
    pdf_link = re.findall('/sites.+\.pdf', str(url))
    if len(pdf_link)>0:
      pdf_link=str(pdf_link)
      pdf_link=pdf_link.replace('[','').replace('\'','').replace(']','')
      pdf_link='https://www.gafspfund.org/'+str(pdf_link)
      print(pdf_link)
  except:
    pass

  if len(pdf_link) > 0:
    pdf_response = requests.get(pdf_link)
    print('PDF Title:')
    filename = unquote(pdf_response.url).split('/')[-1]
    print(filename, '\n')
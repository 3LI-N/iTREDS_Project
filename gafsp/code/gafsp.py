import requests 
from bs4 import BeautifulSoup 
import re 
import os 
from urllib.request import unquote

# step 1: get to project page per year
def get_list_of_years():
  gafsp_url='https://www.gafspfund.org/projects' 
  response = requests.get(gafsp_url) 
  content = BeautifulSoup(response.text, 'lxml')

  l=content.find('div', class_='form-item js-form-item form-group form-type-select js-form-type-select form-item-call-for-proposal js-form-item-call-for-proposal form-no-label') 
  year_lines=l.find_all('option') 
  years=[] 
  for year_line in year_lines[1:]: 
    try: 
      year = re.findall('>.*<', str(year_line)) 
      if len(year)>0: 
        year=str(year) 
        year=year.replace('['>', '').replace('<']', '') 
        year=int(year)
        if year>=2015:
          years.append(year)
    except:
      pass
  return years

def get_project_documents(years):

  #concatenate each year to this link 
  url='https://www.gafspfund.org/projects?location=All&funding=All&supervising=All&field_project_status_target_id=All&call_for_proposal=' 
  url_end='&field_regional_value=0&page=' 
  page_number=0 
  max_pages=1

  for year in years: 
    while page_number<=max_pages: projects_url=url+str(year)+url_end+str(page_number) 
    response = requests.get(projects_url) 
    content = BeautifulSoup(response.text, 'lxml') 
    l=content.find('div',class_='projects-grid mh') 
    if l: 
      links=l.find_all('a')
      # getting project links by calling the get_project_links function
      urls=get_project_links(links)
      # getting pdf document links under every project
      get_pdf_links(urls)
      page_number=page_number+1
    else:
      page_number=0
      break
def get_project_links(links):

#save project links in urls 
  urls=[] 
  for link in links: 
    try: 
      project_link = re.findall('href=".+', str(link)) 
      if len(project_link)>0: 
        project_link=str(project_link) 
      project_link=project_link.replace('[\'href="/', '').replace('">\']','') 
      project_link='https://www.gafspfund.org/'+project_link 
      urls.append(project_link) 
      pass 
    except: 
        pass 
  return urls

def get_pdf_links(urls):

  for url in urls: 
    response = requests.get(url) 
    content = BeautifulSoup(response.text, 'lxml') 
    pdf_urls = content.find_all('a')

  for pdf_url in pdf_urls:
    try:
      pdf_link = re.findall('/sites.+\.pdf', str(pdf_url))
      if len(pdf_link)>0:
        pdf_link=str(pdf_link)
        pdf_link=pdf_link.replace('[\'/','').replace('\']','')
        pdf_link='https://www.gafspfund.org/'+str(pdf_link)

    except:
      pass

    if len(pdf_link) > 0:
      pdf_response = requests.get(pdf_link)
      filename = (unquote(pdf_response.url).split('/')[-1]).strip('.pdf')
      pdf_filename = filename + ".pdf"
      # txt_filename = filename + ".txt"

      try:
        with open('./' + pdf_filename, 'wb') as f:
          f.write(pdf_response.content)
        print("PDF generated: " + pdf_filename)

      except:
        print("Encountered issue downloading PDF and extracting txt")
        pass
def main(): 
  years=get_list_of_years() 
  get_project_documents(years)

main()
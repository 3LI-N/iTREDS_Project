#link = https://www.afdb.org/en/projects-and-operations?name=&field_project_name_value=&items_per_page=60

import requests
from bs4 import BeautifulSoup
import re
from urllib.request import unquote
import os



class Project:
	def __init__(self, title, country, year, id, url):
		self.title = title
		self.country = country
		self.year = year
		self.id = id
		self.url = url
		self.doc_link = ''


def get_project_urls():
	project_urls = []
	cont_scraping = True
	page = 0
	while cont_scraping:
		if page > 5: # adding this if statement only for testing purposes so it doesn't take forever to read in projects
			break
		cont_scraping = False
		url = 'https://www.afdb.org/en/projects-and-operations?name=&field_project_name_value=&items_per_page=60'
		if page > 0:
			url += '&page=' + str(page)
		response = requests.get(url)
		if response == None:
			break
		content = BeautifulSoup(response.text, 'lxml')

		a_tags = content.find_all('a')

		for tag in a_tags:
			id_match = re.findall('\>P\-[A-Z0-9][A-Z0-]\-[A-Z0-9][A-Z0-9][A-Z0-9]\-[0-9][0-9][0-9]\<', str(tag))
			if len(id_match) > 0:
				cont_scraping = True
				project_id = id_match[0][1:-1].lower()
				project_url = 'https://www.afdb.org/en/projects-and-operations/' + project_id
				project_urls.append(project_url)
				#print(project_id)

		page += 1

	return project_urls



def main():
	project_urls = get_project_urls()
	print(project_urls)


if __name__=="__main__":
	main()
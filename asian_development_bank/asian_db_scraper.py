# link = https://www.adb.org/projects/sector/agriculture-natural-resources-and-rural-development-1057

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

	def print_data(self):
		print("Title: {}".format(self.title))
		print("Country: {}".format(self.country))
		print("Year: {}".format(str(self.year)))
		print("ID: {}".format(self.id))
		print("Url: {}".format(self.url))


def get_projects(oldest_year):
	projects = []
	cont_scraping = True
	page = 0
	while True:
		url = 'https://www.adb.org/projects/sector/agriculture-natural-resources-and-rural-development-1057'
		if page > 0:
			url += '?page=' + str(page)
		response = requests.get(url)
		if response == None:
			break
		content = BeautifulSoup(response.text, 'lxml')

		div_tags = content.find_all('div')

		for tag in div_tags:
			try:
				if(tag['class'][0] == 'item'):
					proj_year = int(re.search(r"dc:date[^<]+", str(tag)).group()[-4:])
					if proj_year < oldest_year:
						return projects
					proj_country = re.search(r";[^;]+;", str(tag)).group()[2:-1]
					proj_title = tag.a.text
					proj_link = "https://www.adb.org" + str(tag.a['href'])
					proj_id = proj_link[-14:-5]

					new_project = Project(proj_title, proj_country, proj_year, proj_id, proj_link)
					projects.append(new_project)
			except:
				pass

		page += 1

	return projects



def main():
	projects = get_projects(2015)
	for proj in projects:
		proj.print_data()
		print()

	print(len(projects))


if __name__=="__main__":
	main()


# no tar: https://www.adb.org/projects/44328-013/main
# with tar and completion tar: https://www.adb.org/projects/50058-001/main
# another tar example: https://www.adb.org/projects/49004-001/main


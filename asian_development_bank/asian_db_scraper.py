# link = https://www.adb.org/projects/sector/agriculture-natural-resources-and-rural-development-1057/type/sovereign-1069?terms=&sort_by=field_date_content&sort_order=DESC&page=0
# https://www.adb.org/projects/sector/agriculture-natural-resources-and-rural-development-1057/type/sovereign-1069?terms=&sort_by=field_date_content&sort_order=DESC&page=0

import requests
from bs4 import BeautifulSoup
import re
from urllib.request import unquote
import os
import csv


def download_doc(url, doc_type, proj_id):
	response = requests.get(url)
	if response == None:
		return 1

	content_type = response.headers.get('content-type')

	if 'application/pdf' in content_type:
		pdf_filename = proj_id + '-' + doc_type + '.pdf'
		txt_filename = doc_type + '/' + proj_id + '-' + doc_type + '.txt'
		try:
			with open('./' + pdf_filename, 'wb') as f:
				f.write(response.content)
			print("PDF generated: " + pdf_filename)
			txt_gen_return = os.system("pdf2txt.py ./" + pdf_filename + " > ./txt_files/" + txt_filename) #256 for error, 0 for okay
			os.system("sed '/^\s*$/d' -i txt_files/" + txt_filename) # removes blank lines
			print("txt generated: " + txt_filename)
			os.system("rm ./" + pdf_filename) # saves space by deleting the pdf
			print("PDF deleted")
			if int(txt_gen_return) != 0:
				os.system("rm ./" + txt_filename)
				print("Error in generating txt: faulty txt deleted")
			return int(txt_gen_return)
		except:
			print("Encountered issue downloading PDF and extracting txt")

	return 1


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

	def download_txt(self):
		with open('pam_docs.txt') as pam_docs:
			if self.id in pam_docs.read():
				print('Already downloaded PAM')
				return 0

		if download_doc(self.url, 'pam', self.id) == 0:
			return 0

		second_url = 'https://www.adb.org/sites/default/files/project-documents//' + str(self.id) + '-pam.pdf'

		if download_doc(second_url, 'pam', self.id) == 0:
			return 0
		
		print('No PAM, checking for RRP')

		self.url = self.url.replace('pam', 'rrp')

		with open('rrp_docs.txt') as rrp_docs:
			if self.id in rrp_docs.read():
				print('Already downloaded RRP')
				return 0

		if download_doc(self.url, 'rrp', self.id) == 0:
			return 0

		second_url = second_url.replace('pam', 'rrp')

		if download_doc(second_url, 'rrp', self.id) == 0:
			return 0

		return 1


'''def get_projects(oldest_year):
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
			print(tag)
			print()
		return []

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
					new_project.print_data()
					print()
			except:
				pass

		page += 1

	return projects
'''

def get_projects():
	projects = []
	with open('asian_development_bank_projects.csv', mode ='r')as file:
		csvFile = csv.reader(file)
		first_line = True
		for lines in csvFile:
			if first_line:
				first_line = False
			else:
				pam_link = 'https://www.adb.org/sites/default/files/project-documents/' + lines[0][:5] + '/' + lines[0] + '-pam-en.pdf'
				new_project = Project(lines[1], lines[2], int(lines[7][-4:]), lines[0], pam_link)
				projects.append(new_project)
				

	return projects

def main():
	projects = get_projects()

	num_documents = 0
	for proj in projects:
		if proj.download_txt() == 0:
			num_documents += 1

	print()
	print(str(num_documents) + ' of ' + str(len(projects)) + ' scraped')

	


if __name__=="__main__":
	main()


# no pam: https://www.adb.org/sites/default/files/project-documents/50165/50165-002-pam-en.pdf
#			https://www.adb.org/sites/default/files/project-documents/38412/38412-033-pam-en.pdf

# has pam: https://www.adb.org/sites/default/files/project-documents/50278/50278-002-pam-en.pdf



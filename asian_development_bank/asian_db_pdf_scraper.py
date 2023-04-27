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
		pdf_filename = "pdf_files/" + doc_type + '/' + proj_id + '-' + doc_type + '.pdf'
		try:
			with open('./' + pdf_filename, 'wb') as f:
				f.write(response.content)
			print("\tPDF generated: " + pdf_filename)
			return 0
		except:
			print("\tEncountered issue downloading PDF and extracting txt")

	return 1

def download_type(base_url, doc_type, proj_id):
	if download_doc(base_url, doc_type, proj_id) == 0:
		return 0

	if download_doc(base_url.replace('-en.pdf', '.pdf'), doc_type, proj_id) == 0:
		return 0

	if download_doc(base_url.replace('pdf', 'PDF'), doc_type, proj_id) == 0:
		return 0

	if download_doc(base_url.replace('-en.pdf', '.PDF'), doc_type, proj_id) == 0:
		return 0

	second_url = 'https://www.adb.org/sites/default/files/project-documents//' + str(proj_id) + '-' + doc_type + '.pdf'

	if download_doc(second_url, doc_type, proj_id) == 0:
		return 0

	if download_doc(second_url.replace('.pdf', '-en.pdf'), doc_type, proj_id) == 0:
		return 0

	if download_doc(second_url.replace('pdf', 'PDF'), doc_type, proj_id) == 0:
		return 0

	if download_doc(second_url.replace('.pdf', '-en.PDF'), doc_type, proj_id) == 0:
		return 0
	
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

	def download_pdf(self):

		if download_type(self.url, 'pam', self.id) == 0:
			return 0
		
		print('\tNo PAM, checking for RRP')

		self.url = self.url.replace('pam', 'rrp')

		if download_type(self.url, 'rrp', self.id) == 0:
			return 0

		print('\tNo RRP, checking for PFRTR')

		self.url = self.url.replace('rrp', 'pfrtr')

		if download_type(self.url, 'pfrtr', self.id) == 0:
			return 0
		
		print('\tNo PFRTR')

		return 1


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
	for i, proj in enumerate(projects):
		print(str(i+1) + ' of ' + str(len(projects)) + ':')
		if proj.download_pdf() == 0:
			num_documents += 1

	print()
	print(str(num_documents) + ' of ' + str(len(projects)) + ' scraped')

	


if __name__=="__main__":
	main()


# no pam: https://www.adb.org/sites/default/files/project-documents/50165/50165-002-pam-en.pdf
#			https://www.adb.org/sites/default/files/project-documents/38412/38412-033-pam-en.pdf

# has pam: https://www.adb.org/sites/default/files/project-documents/50278/50278-002-pam-en.pdf



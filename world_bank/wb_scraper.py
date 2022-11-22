import requests
from bs4 import BeautifulSoup
import re
from urllib.request import unquote
import os
import csv


def get_doc_urls(oldest_year):
	doc_urls = []
	with open('wb_projects.csv', mode ='r')as file:
		csvFile = csv.reader(file)
		for lines in csvFile:
			if len(lines[7]) > 0:
				try:
					year = int(lines[7][:4])
					if year >= oldest_year:
						doc_url = lines[6].replace('project-detail', 'document-detail') + '?type=projects'
						doc_urls.append(doc_url)
				except:
					pass
				

	return doc_urls

def get_txt_url(url):
	response = requests.get(url)
	#http_match = re.findall('href=\"http://documents\.worldbank\.org/.+\"', response.text)
	http_match = re.findall('table', response.text)
	if len(http_match) > 0:
		print(http_match[0])
	'''content = BeautifulSoup(response.text, 'lxml')

	td_tags = content.find_all('table')
	for tag in td_tags:
		print(tag)'''

	print(response.text)


def main():
	doc_urls = get_doc_urls(2015)
	#print(doc_urls)
	test_index = 5
	print(doc_urls[test_index] + '\n')
	get_txt_url(doc_urls[test_index])


if __name__=="__main__":
	main()
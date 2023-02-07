import requests
from bs4 import BeautifulSoup
import re
from urllib.request import unquote
import os
import csv

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver import FirefoxOptions

#url = 'https://projects.worldbank.org/en/projects-operations/document-detail/P148733?type=projects'


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
	# initiating the webdriver. Parameter includes the path of the webdriver.
	opts = FirefoxOptions()
	opts.add_argument("--headless")
	driver = webdriver.Firefox(options=opts)
	driver.get(url) 
	
	# this is just to ensure that the page is loaded
	time.sleep(5) 
	
	html = driver.page_source

	content = BeautifulSoup(html, "html.parser")

	tr_tags = content.find_all('tr')
	for tag in tr_tags:
		try:
			txt_url = tag.a['href']
			tag_td = tag.find_all('td')
			doc_type = re.findall(">Project Information Document</td", str(tag_td[3]))
			if len(doc_type) > 0:
				return txt_url
		except:
			pass
	return ""
	'''tag = tr_tags[5]
	print(tag.a['href'])
	tag_td = tag.find_all('td')
	print(tag_td[3])
	doc_type = re.findall(">Procurement Plan</td", str(tag_td[3]))
	if len(doc_type) > 0:
		print(doc_type[0])
	else:
		print('not working')'''
	#print(len(tr_tags))
	#print(tr_tags[5])


def main():
	doc_urls = get_doc_urls(2015)
	#print(doc_urls)
	txt_urls = []
	for i, doc_url in enumerate(doc_urls):
		if i > 10:
			return
		txt_url = get_txt_url(doc_url)
		if txt_url != "":
			txt_urls.append(txt_url)
			print(txt_url)
		else:
			print("no txt url")
	#txt_url = get_txt_url('https://projects.worldbank.org/en/projects-operations/document-detail/P148733?type=projects')
	#print(txt_url)


if __name__=="__main__":
	main()
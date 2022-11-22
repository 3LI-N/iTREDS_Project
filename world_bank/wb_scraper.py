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


def main():
    print('main idk')


if __name__=="__main__":
	main()
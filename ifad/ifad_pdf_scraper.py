'''
Issues:
- there are supervision/implementation docs and mid-term docs
- ex: [108] https://www.ifad.org/en/web/operations/-/project/2000001184

'''

import requests
from bs4 import BeautifulSoup
import re
from urllib.request import unquote
import os
import csv


class Project:
	def __init__(self, title, country, year, id, url):
		self.title = title
		self.country = country
		self.year = year
		self.id = id
		self.url = url
		self.doc_link = ''
		self.has_pres_report = False


	def print_data(self):
		print("Title: " + self.title)
		print("Country: " + self.country)
		print("Year: " + self.year)
		print("ID: " + self.id)
		print("Url: " + self.url)
		if self.doc_link == '':
			print("There is no report link")
		elif self.has_pres_report:
			print("President's Report link: " + self.doc_link)
		else:
			print("Project Design Report link: " + self.doc_link)


	def get_filename(self):
		filename = self.country + "_" + self.year + "_" + self.id
		return filename.replace(" ", "-").lower()


	def get_report_link(self):
		response = requests.get(self.url)
		content = BeautifulSoup(response.text, 'html.parser')

		a_tags = content.find_all('a')
		for tag in a_tags:
			try:
				http_match = re.findall('https://www\.ifad\.org.+', tag['href'])
				if len(http_match) == 0:
					continue
				link_texts = tag.find_all('strong')
				if len(link_texts) == 0:
					continue

				for text in link_texts:
					cmp_text = str(text).replace("’","'").lower()
					if "president's report" in cmp_text:
						self.doc_link = http_match[0]
						self.has_pres_report = True
						return
					elif "design" in cmp_text:
						if self.doc_link == '':
							self.doc_link = http_match[0]
			except:
				pass
		if len(self.doc_link) > 0:
			return

		# if any specific link doesn't contain the doc description the div above might
		div_tags = content.find_all('div')
		for tag in div_tags:
			try:
				if tag['class'][0] == 'col-lg-7' and tag['class'][1] == 'col-md-12':
					http_match = re.findall('https://www\.ifad\.org[^\"]+', str(tag))
					if len(http_match) == 0:
						continue
					cmp_text = str(tag).replace("’","'").lower()
					if "president's report" in cmp_text:
						self.doc_link = http_match[0]
						self.has_pres_report = True
						return
					elif "design" in cmp_text or "pdr" in cmp_text:
						if self.doc_link == '':
							self.doc_link = http_match[0]
			except:
				pass


	def download_pdf(self):
		if self.doc_link == '':
			print("Couldn't find a report")
			return
		if self.has_pres_report:
			print("Downloading President's Report")
		else:
			print("Downloading Project Design Report")

		response = requests.get(self.doc_link)
		content = BeautifulSoup(response.text, 'html.parser')

		pdf_urls = content.find_all('button')

		pdf_link = ''
		for url in pdf_urls:
			try:
				full_http_match = re.findall('https.+\.pdf', url['onclick'])
				if len(full_http_match) > 0:
					pdf_link = full_http_match[0]
				else:
					partial_http_match = re.search(r"window.open\(\'(.+)\',", url['onclick'])
					if partial_http_match != None:
						pdf_link = 'https://ifad.org' + partial_http_match.group(1)
			except:
				pass


		if len(pdf_link) > 0:
			pdf_response = requests.get(pdf_link)
			filename = str(self.get_filename())
			pdf_filename = filename + ".pdf"
			if self.has_pres_report:
				pdf_filename = "pres_reports/" + pdf_filename
			else:
				pdf_filename = "dsgn_reports/" + pdf_filename

			try:
				with open('./pdf_files/' + pdf_filename, 'wb') as f:
					f.write(pdf_response.content)
				print("PDF generated: " + pdf_filename)
				return 0
			except:
				print("Encountered issue downloading PDF")
				pass
		return 1


def get_projects():
	projects = []
	with open('ifad_metadata.csv', mode ='r')as file:
		csvFile = csv.reader(file)
		first_line = True
		for lines in csvFile:
			if first_line:
				first_line = False
			else:
				new_project = Project("", lines[2], lines[4], lines[0], "https://www.ifad.org/en/web/operations/-/project/" + lines[0])
				projects.append(new_project)
	return projects


def main():

	projects = get_projects()

	report_projects = []
	no_report_projects = []

	num_pres = 0
	num_dsgn = 0

	for i, project in enumerate(projects):
		project.get_report_link()
		if project.doc_link == '':
			no_report_projects.append(project)
			print(str(i) + "\tno report")
		else:
			report_projects.append(project)
			if project.has_pres_report:
				print(str(i) + "\tpresident's report")
				num_pres += 1
			else:
				print(str(i) + "\tproject design report")
				num_dsgn += 1
	print()

	num_failed = 0
	for project in report_projects:
		download_outcome = project.download_pdf()
		if download_outcome != 0:
			num_failed += 1
			no_report_projects.append(project)
			if project.has_pres_report:
				num_pres -= 1
			else:
				num_dsgn -= 1

if __name__=="__main__":
    main()


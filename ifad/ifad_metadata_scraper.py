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
		self.status = ""
		self.project_amount = 0 # project_amount and commitment amount in US$ million
		self.commitment_amount = 0
		self.financing_terms = ""
		# cannot determine the following values but needed in spreadsheet:
		self.region = ""
		self.borrower = ""
		self.env_category = ""
		# what report is present
		self.report = "No report"
		# if there is a summary file
		self.has_summary = False
		self.summary = ""


	def print_data(self):
		print("Title: " + self.title)
		print("Country: " + self.country)
		print("Year: " + self.year)
		print("ID: " + self.id)
		print("Url: " + self.url)
		print("Status: " + self.status)
		print("Total Project Amount: $" + str(self.project_amount) + " million")
		print("Commitment Amount: $" + str(self.commitment_amount) + " million")
		print("Financing Terms: " + self.financing_terms )
		print("Region: " + self.region)
		print("Borrowing Entity: " + self.borrower)
		print("Environmental Category: " + self.env_category)
		


	def get_filename(self):
		filename = self.country + "_" + self.year + "_" + self.id
		return filename.replace(" ", "-").lower()


	def get_metadata(self):
		# want status, total project amount, ifad financing (commitment amount), financing terms?
		response = requests.get(self.url)
		content = BeautifulSoup(response.text, 'lxml')

		main_content = content.find('div', class_="main-content")
		summary_match = re.findall(">[^<]+<", str(main_content).replace('\n', ''))
		if len(summary_match) > 0:
			self.has_summary = True
			for para in summary_match:
				self.summary += str(para)[1:-1] + '\n'

		d_tags = content.find_all('dd')
		result = 0

		#print(len(d_tags))
		status_match = re.findall('Status:[a-zA-Z]+', ''.join(str(d_tags[0]).split()))
		if len(status_match) > 0:
			#print("Status: " + status_match[0][7:])
			self.status = status_match[0][7:]
		else:
			print(self.id + " status not working")
			result = 1

		proj_amt_match = re.findall('US\$[0-9]+\.?[0-9]*', ''.join(str(d_tags[5]).split()))
		if len(proj_amt_match) > 0:
			self.project_amount = float(proj_amt_match[0][3:])
			#print("Total Project Amount: " + str(self.project_amount))
		else:
			print(self.id + " total project amount not working")
			result = 1

		comm_amt_match = re.findall('US\$[0-9]+\.?[0-9]*', ''.join(str(d_tags[6]).split()))
		if len(comm_amt_match) > 0:
			self.commitment_amount = float(comm_amt_match[0][3:])
			#print("Commitment Amount: " + str(self.commitment_amount))
		else:
			print(self.id + " commitment amount not working")
			result = 1

		fin_terms_match = re.findall('\> [a-zA-Z].+ \<', ' '.join(str(d_tags[-3]).split()))
		if len(fin_terms_match) > 0:
			self.financing_terms = fin_terms_match[0][2:-2]
			#print("Financing terms: " + self.financing_terms)
		else:
			print(self.id + " financing terms not working")
			result = 1

		with open(r'pres_report_files.txt', 'r') as fp:
			lines = fp.readlines()
			for row in lines:
				word = self.get_filename()
				if row.find(word) != -1:
					self.report = "President's Report"
					break

		if self.report != "President's Report":
			with open(r'dsgn_report_files.txt', 'r') as fp:
				lines = fp.readlines()
				for row in lines:
					word = self.get_filename()
					if row.find(word) != -1:
						self.report = "Project Design Report"
						break

		return result

	def write_summary_file(self):
		if self.has_summary:
			filename = 'summary_' + str(self.get_filename()) + '.txt'
			with open('./txt_files/summary/' + filename, 'w') as f:
				f.write(self.summary)


	def get_csv_row(self, with_summary):
		if with_summary:
			return [self.id, self.status, self.country, self.region, self.year, self.borrower, self.project_amount, self.commitment_amount, self.env_category, self.report, str(self.summary)]
		return [self.id, self.status, self.country, self.region, self.year, self.borrower, self.project_amount, self.commitment_amount, self.env_category, self.report, str(self.has_summary)]

	

def get_valid_project_urls(oldest_year):
	url = 'https://www.ifad.org/en/web/operations/projects-and-programmes'
	response = requests.get(url)
	content = BeautifulSoup(response.text, 'lxml')

	a_tags = content.find_all('a')
	projects = []

	for tag in a_tags:
		try:
			http_match = re.findall('https://www\.ifad\.org/en/web/operations/.+', tag['href'])
			if len(http_match) == 0:
				continue
			project_values = tag.find_all('div')
			project_title = re.search(r">(.+)<", str(project_values[1])).group(1)
			project_id = re.search(r">([0-9]+)<", str(project_values[2])).group(1)
			project_country = re.search(r">(.+)<", str(project_values[3])).group(1)
			project_year = re.search(r"([0-9][0-9][0-9][0-9])<", str(project_values[4])).group(1)

			if int(project_year) >= oldest_year:
				new_project = Project(project_title, project_country, project_year, project_id, http_match[0])
				projects.append(new_project)
		except:
			pass

	return projects



def main():

	current_projects = get_valid_project_urls(2015)

	print("Number of projects: " + str(len(current_projects)))
	print()

	working_projects = []
	error_projects = []
	for i, proj in enumerate(current_projects):
		print()
		print("Project {} of {}".format(str(i+1), str(len(current_projects))))
		if proj.get_metadata() > 0:
			error_projects.append(proj)
			print("Error scraping metadata")
		else:
			working_projects.append(proj)
			proj.write_summary_file()
			proj.print_data()

	with open('ifad_metadata.csv', 'w') as csvfile:
		filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
		filewriter.writerow(['Project ID', 'Status', 'Country', 'Region', 'Year approved', 'Borrowing entity', 'Project amount (total)', 'Committment amount', 'Environmental category', 'Report', 'Has summary'])
		for proj in working_projects:
			#proj_row = proj.get_csv_row()
			filewriter.writerow(proj.get_csv_row(False))
	
	with open('aws_ifad_metadata.csv', 'w') as csvfile:
		filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
		filewriter.writerow(['Project ID', 'Status', 'Country', 'Region', 'Year approved', 'Borrowing entity', 'Project amount (total)', 'Committment amount', 'Environmental category', 'Report', 'Summary'])
		for proj in working_projects:
			#proj_row = proj.get_csv_row()
			filewriter.writerow(proj.get_csv_row(True))


if __name__=="__main__":
    main()


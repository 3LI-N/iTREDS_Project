'''
This code reads in ifad_metadata.csv if it exists, and updates it by checking for reports for all reportless projects

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
		filename = str(self.country) + "_" + str(self.year) + "_" + str(self.id)
		return filename.replace(" ", "-").lower()


	def get_report_link(self):
		response = requests.get(self.url)
		content = BeautifulSoup(response.text, 'lxml')

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


	def download_txt(self):
		if self.doc_link == '':
			print("Couldn't find a report")
			return
		if self.has_pres_report:
			print("Downloading President's Report")
		else:
			print("Downloading Project Design Report")

		response = requests.get(self.doc_link)
		content = BeautifulSoup(response.text, 'lxml')

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
			txt_filename = filename + ".txt"
			if self.has_pres_report:
				txt_filename = "pres_reports/" + txt_filename
			else:
				txt_filename = "dsgn_reports/" + txt_filename

			try:
				with open('./' + pdf_filename, 'wb') as f:
					f.write(pdf_response.content)
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
				pass
		return 1


	def get_metadata(self):
		# want status, total project amount, ifad financing (commitment amount), financing terms?
		response = requests.get(self.url)
		content = BeautifulSoup(response.text, 'lxml')

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


	def get_csv_row(self):
		return [self.id, self.status, self.country, self.region, self.year, self.borrower, self.project_amount, self.commitment_amount, self.env_category, self.report]


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

	prev_table_entries = dict()
	#prev_proj_ids = []

	with open('ifad_metadata.csv', mode ='r')as file:
		csvFile = csv.reader(file)
		for line in csvFile:
			prev_table_entries[line[0]] = line
			#prev_table_entries.append(line)
			#prev_proj_ids.append(line[0])
			#print(line[0])

	current_projects = get_valid_project_urls(2015)
	print(len(current_projects))
	report_projects = []

	for project in current_projects:
		if project.id not in prev_table_entries.keys():
			print("Adding project " + str(project.id))
			project.get_report_link()
			if project.doc_link != '':
				report_projects.append(project)
	
	for key in prev_table_entries.keys():
		if prev_table_entries[key][-1] == "No report":
			project = Project("", str(prev_table_entries[key][2]), int(prev_table_entries[key][4]), int(prev_table_entries[key][0]), "https://www.ifad.org/en/web/operations/-/project/" + str(prev_table_entries[key][0]))
			print("Rechecking for report from project " + str(project.id))
			project.get_report_link()
			if project.doc_link != '':
				report_projects.append(project)

	for i, project in enumerate(report_projects):
		print("Downloading " + str(i+1) + " of " + str(len(report_projects)))
		project.download_txt()

	'''working_projects = []
	error_projects = []
	for i, proj in enumerate(current_projects):
		print("\nScrapping metadata from " + str(i) + " of " + str(len(current_projects)))
		if proj.get_metadata() > 0:
			error_projects.append(proj)
			print("Error scraping metadata")
		else:
			working_projects.append(proj)
			proj.print_data()

	with open('ifad_metadata.csv', 'w') as csvfile:
		filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
		filewriter.writerow(['Project ID', 'Status', 'Country', 'Region', 'Year approved', 'Borrowing entity', 'Project amount (total)', 'Committment amount', 'Environmental category', 'Report'])
		for proj in working_projects:
			#proj_row = proj.get_csv_row()
			filewriter.writerow(proj.get_csv_row())'''

if __name__=="__main__":
    main()


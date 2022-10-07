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
					elif "design" in cmp_text:
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
			try:
				with open('./' + pdf_filename, 'wb') as f:
					f.write(pdf_response.content)
				print("PDF generated: " + pdf_filename)
				os.system("pdf2txt.py ./" + pdf_filename + " > ./txt_files/" + txt_filename)
				os.system("sed '/^\s*$/d' -i txt_files/" + txt_filename) # removes blank lines
				print("txt generated: " + txt_filename)
				os.system("rm ./" + pdf_filename) # saves space by deleting the pdf
				print("PDF deleted")
				return 0
			except:
				print("Encountered issue downloading PDF and extracting txt")
				pass
		return 1


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

	'''for project in projects:
		project.printData()
		print()'''
	return projects

current_projects = get_valid_project_urls(2015)

print("Number of projects: " + str(len(current_projects)))
print()

report_projects = []
no_report_projects = []

num_pres = 0
num_dsgn = 0

'''for i, project in enumerate(current_projects):
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
print(str(num_pres) + " projects have a president's report")								#103
print(str(num_dsgn) + " projects have a project design report but no president's reprot")	#74
print(str(len(no_report_projects)) + " projects don't have a president's report")			#26
print()'''

'''print("Projects w/o reports:")
for project in no_report_projects:
	print(project.url)'''


test_project = current_projects[83] # [3] is an example with both presidents report and project design report
# using 35 causes an error
test_project.get_report_link()
print()
test_project.print_data()
print()
test_project.download_txt()


'''
Issues:
- there are supervision/implementation docs and mid-term docs
- ex: [108] https://www.ifad.org/en/web/operations/-/project/2000001184

Todo:
- seperate folders for pres report and design report

'''
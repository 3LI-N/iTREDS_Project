import requests
from bs4 import BeautifulSoup
import re
from urllib.request import unquote

class Project:
	def __init__(self, title, country, year, id, url):
		self.title = title
		self.country = country
		self.year = year
		self.id = id
		self.url = url
		self.pres_link = ''
	def print_data(self):
		print("Title: " + self.title)
		print("Country: " + self.country)
		print("Year: " + self.year)
		print("ID: " + self.id)
		print("Url: " + self.url)
		if self.pres_link == '':
			print("There is no President's report link")
		else:
			print("Presidents report link: " + self.pres_link)
	def get_filename(self):
		filename = self.country + "_" + self.year + "_" + self.id + ".pdf"
		return filename.replace(" ", "-").lower()
	def get_presidents_report_link(self):
		response = requests.get(self.url)
		content = BeautifulSoup(response.text, 'lxml')

		a_tags = content.find_all('a')

		for tag in a_tags:
			try:
				http_match = re.findall('https://www\.ifad\.org.+', tag['href'])
				if len(http_match) == 0:
					continue
				#print(tag)
				link_texts = tag.find_all('strong')
				if len(link_texts) == 0:
					continue
				#print(link_texts)

				for text in link_texts:
					cmp_text = str(text).replace("’","'").lower()
					if "president's report" in cmp_text:
						#print('found a match')
						#print(http_match[0])
						self.pres_link = http_match[0]
						return
			except:
				pass


def download_pdf(project):
	# run pdf2txt.py ./pdf/<pdf name> > ./txt_files/<txt name>
	#url = 'https://www.ifad.org/en/-/haiti-2000002247-i-be-project-design-report-november-2021'

	if project.pres_link == '':
		return
	response = requests.get(project.pres_link)
	content = BeautifulSoup(response.text, 'lxml')

	pdf_urls = content.find_all('button')
	#print(pdf_urls)

	#print('\nJust the link:')

	t = 'http'
	pdf_link = ''
	for url in pdf_urls:
		try:
			full_http_match = re.findall('https.+\.pdf', url['onclick'])
			if len(full_http_match) > 0:
				pdf_link = full_http_match[0]
				#print(pdf_link)
			else:
				#print('in this else statement')
				partial_http_match = re.search(r"window.open\(\'(.+)\',", url['onclick'])
				#print('got past here')
				if partial_http_match != None:
					#print('there is a partial http match')
					#print(partial_http_match.group(1))
					pdf_link = 'https://ifad.org' + partial_http_match.group(1)
		except:
			pass

	if len(pdf_link) > 0:
		pdf_response = requests.get(pdf_link)
		filename = project.get_filename()
		print("PDF generated: " + filename)
		with open('./pdf/' + filename, 'wb') as f:
			f.write(pdf_response.content)







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

#pres_report_projects = []
#no_pres_report_projects = []

'''for i, project in enumerate(current_projects):
	project.get_presidents_report_link()
	if project.pres_link == '':
		no_pres_report_projects.append(project)
		print(str(i) + "\tno")
	else:
		pres_report_projects.append(project)
		print(str(i) + "\tyes")
print()
print(str(len(pres_report_projects)) + " projects have a president's report")			#102
print(str(len(no_pres_report_projects)) + " projects don't have a president's report")	#101
'''

test_project = current_projects[40] # [3] is an example with both presidents report and project design report
# using 35 causes an error
test_project.get_presidents_report_link()
print()
test_project.print_data()
print()
if test_project.pres_link == '':
	print("Couldn't find President's Report")
else:
	download_pdf(test_project)
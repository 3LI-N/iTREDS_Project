import csv

class Project:
	def __init__(self, proj_id, title, country, proj_type, status, approval_date, commitment_amount, sector, subsector, env_cat, ip_cat, ir_cat, department, agencies, officer, summary):
		self.proj_id = proj_id
		self.title = title
		self.country = country
		self.proj_type = proj_type
		self.status = status
		self.approval_date = approval_date
		self.commitment_amount = commitment_amount
		self.sector = sector
		self.subsector = subsector
		self.env_cat = env_cat
		self.ip_cat = ip_cat
		self.ir_cat = ir_cat
		self.department = department
		self.agencies = agencies
		self.officer = officer
		self.summary = summary
		self.report = 'No report'

	def get_report(self):
		with open(r'pam_docs.txt', 'r') as fp:
			lines = fp.readlines()
			for row in lines:
				if row.find(self.proj_id) != -1:
					self.report = "Project/Program Administration Manual"
					return
		with open(r'rrp_docs.txt', 'r') as fp:
			lines = fp.readlines()
			for row in lines:
				if row.find(self.proj_id) != -1:
					self.report = "Reports and Recommendations of the President"
					return
		with open(r'pfrtr_docs.txt', 'r') as fp:
			lines = fp.readlines()
			for row in lines:
				if row.find(self.proj_id) != -1:
					self.report = "Tranche Report"
					return

	def get_csv_row(self):
		return [self.proj_id, self.title, self.country, self.proj_type, self.status, self.approval_date, self.commitment_amount, self.sector, self.subsector, self.env_cat, self.ip_cat, self.ir_cat, self.department, self.agencies, self.officer, self.report, self.summary]

def get_projects():
	projects = []
	with open('asian_development_bank_projects.csv', mode ='r')as file:
		csvFile = csv.reader(file)
		first_line = True
		for lines in csvFile:
			if first_line:
				first_line = False
			else:
				new_project = Project(lines[0], lines[1], lines[2], lines[4], lines[5], lines[7], lines[8], lines[10], lines[11], lines[12], lines[13], lines[14], lines[15], lines[16], lines[17], lines[18])
				projects.append(new_project)
				

	return projects


def main():
	projects = get_projects()
	skipped_projects = open("docs_to_remove.txt").readlines()
	with open('adb_metadata.csv', 'w') as csvfile:
		filewriter = csv.writer(csvfile, delimiter=',', quotechar='\"', quoting=csv.QUOTE_MINIMAL)
		filewriter.writerow(['Project ID', 'Title', 'Country', 'Type', 'Project Status', 'Approval Date', 'Committment amount', 'Sector', 'Subsector', 'Environment Assessment Category', 'Indigenous Peoples Category', 'Involuntary Resetllement Category', 'Responsible ADB Department', 'Executing Agencies', 'Responsible ADB Officer', 'Report', 'Abstract Text'])
		for proj in projects:
			skip_this = False
			for skipped_proj in skipped_projects:
				if skipped_proj[:-1] == proj.proj_id:
					skip_this = True
					break
			if skip_this:
				continue
			proj.get_report()
			filewriter.writerow(proj.get_csv_row())

if __name__=="__main__":
    main()


# ID,Title,Country,,Type,Status,,Approval Date,Committment Amount,,Sector,Subsector,Environment Category,Indigenous Peoples Category,Involuntary Resetllement Category,Responsible ADB Department,Executing Agencies,Responsible ADB Officer,Summary
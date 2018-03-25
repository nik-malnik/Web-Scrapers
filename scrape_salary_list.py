import json
import urllib
import urllib2
import csv
import re
import pickle
from os import listdir
from os.path import isfile, join
import time
import lxml.html
import pandas as pd

def Run_Scraping(companies, folder = "Companies"):
	
	filenames = [f for f in listdir("/home/malnik/python_env/Data/SalaryList/" + str(folder) +"/") if isfile(join("/home/malnik/python_env/Data/SalaryList/" + str(folder) +"/", f))]
	
	'''
	response = urllib2.urlopen('http://www.salarylist.com/jobs-salary-by-companies.htm')
	html_page = response.read(response)
	company_list = re.findall(u'\/company\/.*?.htm',html_page)
	'''

	for company in companies:
		
		if str(company) + ".pckl" in filenames:
			print "Already fetched data for " + company
			continue
		print "Starting work on company:" + company	
		company_data = []
		page_num = 0
		while page_num <= 100:
			page_num = page_num + 1
			company_url = 'http://www.salarylist.com/company/' + company + "-Salary.htm?page=" + str(page_num)
			try:
				response = urllib2.urlopen(company_url)
				html_page = response.read(response)
				tree = lxml.html.fromstring(html_page)
				tree = tree.xpath("//table[contains(@class, 'table_1')]")[0]
	
				childrens = tree.getchildren()
				childrens = childrens[1:len(childrens)]
			
				if len(childrens) <= 1:
					print company_url
					break
			
				for children in childrens:
					strings = children.text_content().split('  ')
					strings = [x for x in strings if x]
					company_data.append({ 'company' : company, 'title' : strings[1], 'salary' : strings[2], 'location' : strings[3], 'year' : strings[4], 'info' : strings[5:len(strings)] })
			
			except:
				print company + ":" + str(page_num) + " not found or could not be read\n"
				continue
					
		f = open("/home/malnik/python_env/Data/SalaryList/" + str(folder) +"/" + str(company) + ".pckl", 'wb') 
		try:
			pickle.dump(company_data, f)
		except:
			print "Could not save data \n"
		f.close()

def Run_Scraping_Titles(companies, folder = "Titles", fname = 'title_salary'):
	
	filenames = [f for f in listdir("/home/malnik/python_env/Data/SalaryList/" + str(folder) +"/") if isfile(join("/home/malnik/python_env/Data/SalaryList/" + str(folder) +"/", f))]
	
	'''
	response = urllib2.urlopen('http://www.salarylist.com/jobs-salary-by-companies.htm')
	html_page = response.read(response)
	company_list = re.findall(u'\/company\/.*?.htm',html_page)
	'''
	company_data = []
	for company in companies:
		print "Starting work on company:" + company	
		company_url = 'http://www.salarylist.com/jobs/' + company + "-Salary.htm"
		try:
			response = urllib2.urlopen(company_url)
			html_page = response.read(response)
			tree = lxml.html.fromstring(html_page)
			tree = tree.xpath("//div[contains(@class, 'Google')]")[0].xpath("//dd")
			company_data.append({ 'Title': company,'Low' : tree[0].text_content(), 'Average' : tree[1].text_content(), 'Median' : tree[2].text_content(), 'High' : tree[3].text_content()})
		except:
			print company + " not found or could not be read\n"
			continue
					
	f = open("/home/malnik/python_env/Data/SalaryList/" + str(folder) + "/" + fname + ".pckl", 'wb') 
	try:
		pickle.dump(company_data, f)
	except:
		print "Could not save data \n"
	f.close()
	return company_data

def Run_Scraping_CompanyTitles(companies, folder = "CompanyTitles", fname = 'title_salary'):
	
	filenames = [f for f in listdir("/home/malnik/python_env/Data/SalaryList/" + str(folder) +"/") if isfile(join("/home/malnik/python_env/Data/SalaryList/" + str(folder) +"/", f))]
	
	'''
	response = urllib2.urlopen('http://www.salarylist.com/jobs-salary-by-companies.htm')
	html_page = response.read(response)
	company_list = re.findall(u'\/company\/.*?.htm',html_page)
	'''
	i = 0
	company_data = []
	for company in companies:
		i = i + 1
		print "Starting work on company:" + company['employer'] + ":" + company['title']	
		company_url = 'http://www.salarylist.com/company/' + company['employer'] + "/" + company['title'] + "-Salary.htm"
		try:
			response = urllib2.urlopen(company_url)
			html_page = response.read(response)
			tree = lxml.html.fromstring(html_page)
			tree = tree.xpath("//div[contains(@class, 'Google')]")[0].xpath("//dd")
			company_data.append({ 'employer': company['employer'], 'title': company['title'],'Low' : tree[0].text_content(), 'Average' : tree[1].text_content(), 'Median' : tree[2].text_content(), 'High' : tree[3].text_content()})
		except:
			print str(company) + " not found or could not be read\n"
			continue
		
		if i%100 == 0:
			try:
				pickle.dump(company_data, open("/home/malnik/python_env/Data/SalaryList/" + str(folder) + "/" + fname + ".pckl", 'wb') )
			except:
				print "Could not save data \n"
			
	try:
		pickle.dump(company_data, open("/home/malnik/python_env/Data/SalaryList/" + str(folder) + "/" + fname + ".pckl", 'wb') )
	except:
		print "Could not save data \n"
	return company_data

def Scrape_Company_Role_Page(company,title):
	stats = { 'company' : company, 'title': title }
	url = 'http://www.salarylist.com/company/' + company.replace(" ","-") + '/' + title.strip().replace(" ","-") + '-Salary.htm'
	try:
		response = urllib2.urlopen(url)
		html_page = response.read(response)
	except:
		print "could not fetch the page" + url
		return stats
	
	try:
		tree = lxml.html.fromstring(html_page)
		tree = tree.xpath("//div[@class='Google']")[0]
		tree = tree.xpath("//dl")
		for subtree in tree:
			stats[subtree.xpath("dt/div")[0].text_content()] = subtree.xpath("dd")[0].text_content()
	except:
		print "Issues getting html components:" + url
		return stats
		
	return stats

def Scrape_Company_Salary_Stats(folder = "Companies"):
	mypath = "/home/malnik/python_env/Data/SalaryList/Companies"
	filenames = [f for f in listdir(mypath) if isfile(join(mypath, f))]
	
	mypath = "/home/malnik/python_env/Data/SalaryList/Company_stats"
	filenames_done = [f for f in listdir(mypath) if isfile(join(mypath, f))]
	
	for filename in filenames:
		if filename in filenames_done:
			print filename + " already done"
			continue
		
		f = open( "/home/malnik/python_env/Data/SalaryList/Companies/" + filename, 'rb')
		try:
			temp = pickle.load(f)
			f.close()
		except:
			print "Could not load file " + filename + '\n'
			f.close()
			continue	
		
		titles = []
		for item in temp:
			titles.append(item['title'])
		
		titles = list(set(titles))
		company = filename.split(".")[0]
		print "Fetching " + str(len(titles)) + " titles for company: " + company
		data_stats = []
		for title in titles:
			data_stats.append(Scrape_Company_Role_Page(company,title))
			
		f = open("/home/malnik/python_env/Data/SalaryList/Company_stats/" + str(company) + ".pckl", 'wb') 
		try:
			pickle.dump(data_stats, f)
		except:
			print "Could not save data \n"
		f.close()
		
def Read_Metadata(folder = "Companies"):
	mypath = "/home/malnik/python_env/Data/SalaryList/" + folder
	filenames = [f for f in listdir(mypath) if isfile(join(mypath, f))]
	
	data = []
	for filename in filenames:
		f = open( "/home/malnik/python_env/Data/SalaryList/" + folder + '/' + filename, 'rb')
		try:
			temp = pickle.load(f)
			f.close()
		except:
			print "Could not load file " + filename + '\n'
			f.close()
			continue	
		data = data + temp
	if folder == "Companies":
		for row in data:
			if len(re.findall('[0-9]+',str(row['info']))) > 0:
				row['observations'] = int(re.findall('[0-9]+',str(row['info']))[0])
	
	data = pd.DataFrame(data)
	for col in ['Average','High','Low','Median']:
		data = data[(data[col] != '-') & (data[col].notnull())]
		data[col] = map(lambda a: int(a.replace(',','')) ,data[col])
	data = data[(data['Average'] != data['High']) & (data['High']/data['Low'] < 3)]
	
	temp = pd.DataFrame(data.groupby(['company'])['title'].count())
	data = data[data['company'].isin(temp[temp['title']>5].index)]
	temp1 = pd.DataFrame(data.groupby(['title'])['company'].count())
	data = data[data['title'].isin(temp1[temp1['company']>5].index)]
	return data

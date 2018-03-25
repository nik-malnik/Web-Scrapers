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


def Get_All_Companies():
	
	company_data = []
	
	for page_num in range(1, 1108):
		print "Running for page:" + str(page_num)
		response = urllib2.urlopen('http://www.careerbuilder.com/employerprofile/companysearch.aspx?pg=' + str(page_num) + '&sortby=jobcount')
		html_page = response.read(response)
		tree = lxml.html.fromstring(html_page)
		company_tree =  tree.xpath("//ul")[0]
		for i in range(len(company_tree.xpath("//p[contains(@class, 'compname')]/a/strong"))):
			 company_dict = {'name' :  company_tree.xpath("//p[contains(@class, 'compname')]/a/strong")[i].text_content(),
			 'link' : company_tree.xpath("//p[contains(@class, 'compname')]/a")[i].attrib['href'],
			 'industry' : company_tree.xpath("//p[contains(@class, 'industry')]/strong")[i].text_content()}
			 company_data.append(company_dict)
	'''
	f = open( "/home/malnik/python_env/Data/CareerBuilder/all_companies.pckl", 'wb')
	pickle.dump(company_data, f)
	f.close()
	'''
	return company_data

def Run_Scraping(folder = "Companies"):
	
	filenames = [f for f in listdir("/home/malnik/python_env/Data/CareerBuilder/" + str(folder) +"/") if isfile(join("/home/malnik/python_env/Data/CareerBuilder/" + str(folder) +"/", f))]
	
	f_csv = open( "/home/malnik/python_env/Data/CareerBuilder/all_companies.csv", 'r')
	input_file = csv.DictReader(f_csv, delimiter='\t')
	
	for company in input_file:
		if re.sub('/',' ',company['name']) + ".pckl" in filenames:
			print "Already fetched data for " + company['name']
			continue
		
		print "Running for company:" + company['name']
		try:
			response = urllib2.urlopen(company['link'])
		except:
			print 'could not retreive company page: ' + company['name']
			continue
			 
		html_page = response.read(response)
		tree = lxml.html.fromstring(html_page)
		try:
			company.update({ 'description' : unicode(tree.xpath("//div[contains(@class, 'card company-description')]")[0].text_content()) })
		except:
			print 'could not add description'
		
		tags = ""
		for j in range(len(tree.xpath("//span[contains(@class, 'tag')]"))):
			tags = tags + tree.xpath("//span[contains(@class, 'tag')]")[j].text_content() + "||" 
		company.update({ 'tags' : tags })
			 
		if len(tree.xpath("//a[contains(@class, 'tag clickable')]")) > 0:
			company.update({ 'roles' : tree.xpath("//a[contains(@class, 'tag clickable')]")[0].text_content() }) 
			company.update({ 'roles_url' : tree.xpath("//a[contains(@class, 'tag clickable')]")[0].attrib['href'] }) 
		
		f = open( "/home/malnik/python_env/Data/CareerBuilder/" + folder + "/" + re.sub('/',' ',company['name']) + ".pckl", 'wb')
		
		try:
			pickle.dump(company, f)
		except:
			print "could not save"
		
		f.close()
	
	f_csv.close()

def Read_Metadata(folder = "Companies"):
	mypath = "/home/malnik/python_env/Data/CareerBuilder/" + folder
	filenames = [f for f in listdir(mypath) if isfile(join(mypath, f))]
	
	data = []
	for filename in filenames:
		f = open( "/home/malnik/python_env/Data/CareerBuilder/" + folder + '/' + filename, 'rb')
		try:
			temp = pickle.load(f)
			f.close()
		except:
			print "Could not load file " + filename + '\n'
			f.close()
			continue
			
		if "roles" in temp and len(re.findall("[0-9]+",temp['roles'])) > 0:
			temp['active_jobs'] = int(re.findall("[0-9]+",temp['roles'])[0])
		
		tag_splits = temp['tags'].split('||')
		temp['ownership'] = tag_splits[0]
		del tag_splits[0]
		temp['tags'] = ""
		for ele in tag_splits:
			if " Employees" in ele:
				temp['employee_size'] = ele
			elif "Headquartered in " in ele:
				temp['location'] = ele[17:len(ele)]
			else:
				temp['tags'] = temp['tags'] + "||" + ele
			
		data.append(temp)
	
	data = pd.DataFrame(data)
	return data

import json
import urllib
import urllib2
import csv
import re
import pickle
from os import listdir
from os.path import isfile, join
import time
from bs4 import BeautifulSoup
import pandas as pd
import career_interpret as CI


def Get_Company_List( replace = '+' ):
	
	companies = CI.Get_Company_Names(7193)
	companies = CI.Clean_Company_Names(company_names, replace = replace)
	
	used = []
	companies = [x for x in companies if x not in used and (used.append(x) or True)]
	
	return companies

def Run_Scraping( companies, folder = "Companies" ):
	
	filenames = [f for f in listdir("/home/malnik/python_env/Data/Indeed/" + str(folder) +"/") if isfile(join("/home/malnik/python_env/Data/Indeed/" + str(folder) +"/", f))]
	
	i = 0
	for company in companies:
		i = i + 1
		data = { 'name' : company, 'salary' : [], 'jobtype' : [], 'location' : [], 'level' : [], 'html' : "" }
		
		
		if str(company) + ".pckl" in filenames:
			print "Already fetched data for " + str(i) + ". " + company
			continue
		
		print "Starting work on company:" + str(i) + ". " + company
		
		try:
			response = urllib2.urlopen('http://www.indeed.com/jobs?q=' + company + '&l=')
		except:
			print company + " not found on Indeed\n"
			continue
	
		html_page = response.read(response)
		soup = BeautifulSoup(html_page)
		
		data['htmlsoup'] = soup
		
		salary = soup.find("div", { "id" : "rb_Salary Estimate" })
		salary = re.findall('\$[0-9]{2},000\+ \([0-9]*\)', str(salary))
		data['salary'] = salary
		
		jobtype = soup.find("div", { "id" : "rb_Job Type" })
		jobtype = re.findall('title=[^>]* \([0-9]*\)', str(jobtype))
		data['jobtype'] = jobtype
		
		location = soup.find("div", { "id" : "rb_Location" })
		location = re.findall('title=[^>]* \([0-9]*\)', str(location))
		data['location'] = location
		
		level = soup.find("div", { "id" : "rb_Experience Level" })
		level = re.findall('title=[^>]* \([0-9]*\)', str(level))
		data['level'] = level
		
		time.sleep(1)
		
		f = open("/home/malnik/python_env/Data/Indeed/" + str(folder) +"/" + str(company) + ".pckl", 'wb') 
		try:
			pickle.dump(data, f)
		except:
			print "Could not save data \n"
		f.close()


def Read_Metadata(folder = "Companies"):
	mypath = "/home/malnik/python_env/Data/Indeed/" + folder
	filenames = [f for f in listdir(mypath) if isfile(join(mypath, f))]
	
	data = []
	for filename in filenames:
		f = open( "/home/malnik/python_env/Data/Indeed/" + folder + '/' + filename, 'rb')
		try:
			temp = pickle.load(f)
			f.close()
		except:
			print "Could not load file " + filename + '\n'
			f.close()
			continue
			
		salary_sum = 0
		salary_freq = 0
		for salary in temp['salary']:
			x = re.findall('[0-9,]{1,7}',salary)
			salary_sum = salary_sum + int(re.sub(',', '', x[0]))*int(re.sub(',', '', x[1]))
			salary_freq = salary_freq + int(re.sub(',', '', x[1]))
		
		if salary_freq > 0:
			data.append(dict(temp.items() + {'salary_avg': salary_sum/salary_freq }.items()))
		else:
			data.append(temp)
	
	data = pd.DataFrame(data)
	data = data.drop('htmlsoup',1)
	
	return data

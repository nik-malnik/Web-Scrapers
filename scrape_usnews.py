from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import json
import urllib
import urllib2
import csv
import re
from re import sub
import pickle
import pandas as pd
from os import listdir
from os.path import isfile, join
import time
import lxml.html
import time

'''
http://www.usnews.com/education/best-high-schools/search?magnet=true&public=true
http://www.usnews.com/education/best-high-schools/search?charter=true
http://poetsandquants.com/2012/04/18/u-s-news-historical-mba-rankings/2/

'''

def Get_University_Urls():
	
	html = open('/home/malnik/python_env/Data/usnews/Search _ US News Best Colleges4.html','r').read()
	tree = lxml.html.fromstring(html)
	Blocks = tree.xpath("//h3[contains(@class,'heading-large block-tighter')]/a")
	univ_urls = []
	for Block in Blocks:
		name = Block.text_content()
		univ_urls.append(Block.attrib['href'])

	return univ_urls

def Get_University_Info(univ_urls):
	
	filenames = [f for f in listdir("/home/malnik/python_env/Data/usnews/" + 'universities' +"/") if isfile(join("/home/malnik/python_env/Data/usnews/" + 'universities' +"/", f))]
	browser = webdriver.Firefox()
	get_content = lambda elem: elem.text
	
	for univ_url in univ_urls:
		
		univ = univ_url.split('/')[-1]
		if str(univ) + ".pckl" in filenames:
			print "Already fetched data for " + univ
			continue
		
		print "Starting work on university:" + univ	
		
		try:
			print univ_url + '/overall-rankings'
			browser.get(univ_url + '/overall-rankings')
			time.sleep(10)
		except:
			print "Could not get data"
			continue
		
		try:
			elems = browser.find_element_by_class_name('hero-stats-widget-stats').find_elements_by_tag_name('li')
			stats = map(get_content,elems)
			elems = browser.find_element_by_class_name('block-looser').find_elements_by_class_name('block-flush')
			ranks = map(get_content,elems)
			html = browser.page_source
			Data = { 'name_id' : univ, 'url' : univ_url, 'stats' : stats, 'ranks' : ranks, 'html' : html}
		except:
			print "Could not get components"
			continue
		
		try:
			f = open( '/home/malnik/python_env/Data/usnews/universities/' + univ + '.pckl', 'wb')
			Data = pickle.dump(Data,f)
			f.close()
		except:
			print "Could not save Data"
			continue

def Get_MBA_Ranks():
	files = [
	'Best Business School Rankings _ MBA Program Rankings _ US News1.html',
	'Best Business School Rankings _ MBA Program Rankings _ US News2.html',
	'Best Business School Rankings _ MBA Program Rankings _ US News3.html',
	'Best Business School Rankings _ MBA Program Rankings _ US News4.html'
	]

	names_html = tuitions_html = locations_html = []
	
	for filename in files:
		html = open('/home/malnik/python_env/Data/usnews/' + filename,'r').read()
		tree = lxml.html.fromstring(html)
		names_html = names_html + tree.xpath("//a[@class='school-name']")
		tuitions_html = tuitions_html + tree.xpath("//td[@class='column-odd table-column-odd  search_tuition  ']")
		locations_html = locations_html + tree.xpath("//p[@class='location']")
	
	Data = []
	for i in range(len(names_html)):
		Data.append({'name': names_html[i].text_content().strip(),
		'tuition': tuitions_html[i].text_content().strip(),
		'location': locations_html[i].text_content().strip(),
		'rank': i})
	
	Data = pd.DataFrame(Data)
	Data['name'] = map(lambda x: re.sub(r'[^\x00-\x7F]+',' ', x), Data['name'])
	return Data

def Get_Forbes100():
	filename = '100 Best Companies to Work For - Fortune.html'

	#names_html = tuitions_html = locations_html = []
	
	html = open('/home/malnik/python_env/Data/usnews/' + filename,'rb').read()
	tree = lxml.html.fromstring(html)
	
	names_html = tree.xpath("//span[@class='company-name']")
		
	Data = []
	for i in range(len(names_html)):
		Data.append(names_html[i].text_content().strip())
	
	return Data
			
def Read_Metadata():
	mypath = "/home/malnik/python_env/Data/usnews/universities/"
	filenames = [f for f in listdir(mypath) if isfile(join(mypath, f))]
	
	data = []
	for filename in filenames:
		f = open( "/home/malnik/python_env/Data/usnews/universities/" + filename, 'rb')
		try:
			temp = pickle.load(f)
			f.close()
		except:
			print "Could not load file " + filename + '\n'
			f.close()
			continue	
		#'ROOM AND BOARD'
		#'TOTAL ENROLLMENT'
		#'APPLICATION DEADLINE'
		univ_data = {'name_id' : temp['name_id']}
		if len(re.findall('<title>[a-zA-Z-0-9;&.\' ]+ \|',temp['html'])) > 0:
			univ_data['full_name'] = re.findall('<title>[a-zA-Z-0-9;&.\' ]+ \|',temp['html'])[0][7:-2]
			univ_data['full_name'] = ' '.join([word for word in univ_data['full_name'].split(' ') if word.lower() not in ['overall', 'rankings']])
		for stat in temp['stats']:
			if 'OUT-OF-STATE TUITION & FEES' in stat and len(re.findall('\$[0-9,]+',stat)) > 0:
				univ_data['oos_tuition'] = int(sub(r'[^\d.]', '', re.findall('\$[0-9,]+',stat)[0]))
			elif 'IN-STATE TUITION & FEES' in stat and len(re.findall('\$[0-9,]+',stat)) > 0:
				univ_data['ins_tuition'] = int(sub(r'[^\d.]', '', re.findall('\$[0-9,]+',stat)[0]))
			elif 'TUITION & FEES' in stat and len(re.findall('\$[0-9,]+',stat)) > 0:
				univ_data['tuition'] = int(sub(r'[^\d.]', '', re.findall('\$[0-9,]+',stat)[0]))
			elif 'ROOM AND BOARD' in stat and len(re.findall('\$[0-9,]+',stat)) > 0:
				univ_data['RoomAndBoard'] = int(sub(r'[^\d.]', '', re.findall('\$[0-9,]+',stat)[0]))
			elif 'TOTAL ENROLLMENT' in stat and len(re.findall('[0-9,]+',stat)): 
				univ_data['EnrollmentSize'] = int(sub(r'[^\d.]', '', re.findall('[0-9,]+',stat)[0]))
		'''
		univ_data['ranks'] = ""
		univ_data['ranks_etc'] = ""
		'''
		for rank in temp['ranks']:
			if len(re.findall('[0-9]+', rank)) > 0:
				ranking = re.findall('[0-9]+', rank)[0]
				if 'National Universities' in rank:
					univ_data['Rank_National_Universities'] = ranking
				elif 'Regional Universities' in rank:
					univ_data['Rank_Regional_Universities'] = ranking
				elif 'High School Counselor Rankings' in rank:
					univ_data['Rank_High_School_Counselor'] = ranking
				elif 'Regional Colleges' in rank:
					univ_data['Rank_Regional_Colleges'] = ranking
				elif 'Business Programs' in rank:
					univ_data['Rank_Business_Programs'] = ranking
				elif 'Liberal Arts Colleges' in rank:
					univ_data['Rank_Liberal_Arts_Colleges'] = ranking
				elif 'Veterans' in rank:
					univ_data['Rank_Veterans'] = ranking
				elif 'Public Schools' in rank:
					univ_data['Rank_Public_Schools'] = ranking
				elif 'Value Schools' in rank:
					univ_data['Rank_Value_Schools'] = ranking
				elif 'Undergraduate Engineering' in rank:
					univ_data['Rank_Undergraduate_Engineering'] = ranking
				elif 'Innovative' in rank:
					univ_data['Rank_Innovative'] = ranking
				elif 'Undergraduate Teaching' in rank:
					univ_data['Rank_Undergraduate_Teaching'] = ranking
				'''
				else:
					univ_data['ranks'] = univ_data['ranks'] + '|' + rank
				'''
			else:
				if 'doctorate not offered' in rank:
					univ_data['Is_postgraduate'] = 0
				elif 'degree is a doctorate' in rank:
					univ_data['Is_postgraduate'] = 1
				'''
				else:
					univ_data['ranks_etc'] = univ_data['ranks_etc'] + '|' + rank
				'''
		data.append(univ_data)
	
	data = pd.DataFrame(data)
	return data

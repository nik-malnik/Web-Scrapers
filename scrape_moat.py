import json
import urllib
import urllib2
import csv
import re
import pickle
from os import listdir
from os.path import isfile, join
import time
import msft_cognitive_services as MCS


def Get_Brand_List():
	f = open('/home/malnik/python_env/Data/Moat/brandlist', 'r')
	brands = []
	brand = f.readline()
	while brand:
		 brand = re.sub('[^a-zA-Z0-9 \n\.]{1,2}', '-', brand.strip())
		 brands.append(re.sub(" ", "-",brand.lower()))
		 brand = f.readline()
	
	used = []
	brands = [x for x in brands if x not in used and (used.append(x) or True)]
	
	return brands

def Run_Scraping( brands, Path = "/home/malnik/python_env/Data/Moat",):
	
	'''brands = [ "cheerios", "kellogg-s", "sanyo", "nikon", "gopro", "adidas", "puma", "asics", "casio", "under-armour", "speedo", "cnbc", "fox-news", "cnn", "al-jazeera", "bbc" ]'''

	page_size = 10000
	page_num = 0
	start_date = '2010-1-1'
	end_date = '2017-1-1'


	for brand in brands:
	
		print "Starting work on brand:" + brand + "\n"
	
		try:
			response = urllib2.urlopen('https://moat.com/advertiser/' + brand + '?report_type=display')
		except:
			print brand + " not found on Moat\n"
			continue
		html_page = response.read(response)
		m = re.search(u'loadTime.*\s:\s.[0-9.]*\'',html_page)
		loadtime = re.search(u'[.0-9]+',m.group(0))
		loadtime = loadtime.group(0)
		m = re.search(u'timeHash.*\s:\s.[-0-9.]*\'',html_page)
		hashtime = re.search(u'[-0-9]+',m.group(0))
		hashtime = hashtime.group(0)
	
		creatives = []
		
		dynamic_part = "load_time=" + loadtime + "&time_hash=" + hashtime + "&page=" + str(page_num)
		url="https://moat.com/creatives/advertiser/" + brand + "?report_type=display&start_date=" + start_date + "&end_date=" + end_date + "&period=month&page_size=" + str(page_size) + "&device=desktop&device=mobile&" + dynamic_part
		response = urllib.urlopen(url)
		result = json.load(response)
		print "found " + str(len(result["creative_data"])) + "\n"
		for creative in result["creative_data"]:
			if creative["type"] == "img":
				creatives.append(creative)
				urllib.urlretrieve(creative["path"], Path + "/Images/" + creative["creative_id"])
				if len(creatives)%500 == 0 :
					print "Fetched " + str(len(creatives)) + "\n"
					time.sleep(10) 
		f = open(Path + "/Metadata/" + str(brand) + ".pckl", 'wb')
		pickle.dump(creatives, f)
		f.close()


def Read_Metadata(Path = "Data", analyzeimage = False):
	mypath = Path + "/Moat/Metadata"
	filenames = [f for f in listdir(mypath) if isfile(join(mypath, f))]
	creatives = []
	for filename in filenames:
		f = open( Path + "/Moat/Metadata/" + filename, 'rb')
		creatives.extend(pickle.load(f))
		 
	keys = creatives[0].keys()
	keys.extend([u'thumb_path'])
	with open( Path + '/Moat/VisualAdvertMetadata.csv', 'wb') as output_file:
		dict_writer = csv.DictWriter(output_file, keys)
		dict_writer.writeheader()
		dict_writer.writerows(creatives)


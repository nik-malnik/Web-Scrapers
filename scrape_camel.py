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
import process_amazon_data as PAD

def Run_Scraping():
	brand_data = PAD.Pick_Important_Brands()
	start = 2300 + 1130
	brand_data[start:len(brand_data) - 1]
	count = 0
	for product in brand_data:
		asin = product['asin']
		urllib.urlretrieve('http://charts.camelcamelcamel.com/us/' + str(asin)  + '/amazon.png?force=0&w=4000&h=2000', '/home/malnik/python_env/Data/Camel/Price/' + str(asin) + '.png' )
		count = count + 1
		if count%10 == 0:
			print "Retreived " + str(count) + " asins"

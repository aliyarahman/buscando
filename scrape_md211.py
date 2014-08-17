import requests
from bs4 import BeautifulSoup
import csv
import time
import random



######TODO:
#1) Find all MD211 search terms and populate resources dictionary accordingly
#2) parse the thing they call city, which actually includes city, state, zip and USA
#3) deal with the fact that there are multiple pages of these things - probably have to figure out redirects in requests?



#dictionary of services in the app where values are lists of matching services in MD211

#need to find all relevant searches in MD211

resources = {"food":[],"clothing":[],"legal services":["Legal+Services-Immigrant+Community"],"language":[],
			"medical care":[],"education and enrollment":[],"religious services":[],"transportation":[],
			"counseling":[],"housing":[],"recreation":[],"volunteers":[]}



#build the URL

orgs = {} #a dict of dicts where key is the org name plus the address as a tuple and values are dictionaries containing name, address and each resource

for r in resources:
	for web_name in resources[r]:
		#something about pages here
		page = 1
		url =   "http://www.icarol.info/Search.aspx?org=2046&Count=5&Search={0}\
			&NameOnly=True&pst=Coverage&sort=Proximity&TaxExact=False&Country=United+States\
			&StateProvince=MD&County=-1&City=-1&page={1}".format(web_name, page)

		print(web_name)
		time.sleep(random.randint(1,5))
		response = requests.get(url)
		soup = BeautifulSoup(response.text)
		#print(soup.prettify())
		
		#the website doesn't seem to have a container that holds both the name of the org and the
		#contact info together, so we're counting on them being in the same order.
		header_info = soup.findAll('td',attrs={"class":"DetailsHeader"})
		address_info = soup.findAll('td',attrs={"class":"SearchDetails"})
		#maybe should throw an error if they're not the same length
		
		for i in range(len(header_info)):
			h = header_info[i].text.strip()
			a = address_info[i]
			org_name = h[h.find("Agency")+8:]
			address_label = "rptSearchResults_lblAddress_{0}".format(i)
			address = a.find('span', attrs={"id":address_label}).text.strip()
			city = a.find('span', attrs={"id":"rptSearchResults_lblCity_{0}".format(i)}).text.strip() #this is actually city, state, zip and country and needs to be parsed
			phone = a.find('span', attrs={"id":"rptSearchResults_lblPhone_{0}".format(i)}).text.strip("Phone:").strip()
			
			website_label = "rptSearchResults_hlAgencyName_{0}".format(i)
			website = a.find('a',attrs={"id":website_label}).text.strip()

			
			org_key = (org_name,address)
			
			if org_key not in orgs:
				orgs[org_key] = {"provider_name":org_name,"address1":address,"city":city,"phone":phone,"website":website}
			
			orgs[org_key][r] = "yes"
			
			
			
		
		print(len(header_info))
		print(len(address_info))



#dump dictionary to a properly formatted csv

csv_header = ["provider_name","location_name","image","website","address1","address2","city","state",
			"zipcode","contact","phone","hours","food","clothing","legal services","language",
			"medical care","education and enrollment","religious services","transportation",
			"counseling","housing","recreation","volunteers","other"]



with open("providers_from_md211.csv","wb") as provider_csv:
	w = csv.DictWriter(provider_csv, csv_header)
	for key,value in orgs.iteritems():
		w.writerow(value)
	

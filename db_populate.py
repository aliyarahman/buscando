from django.contrib.auth.models import User
from app.views import *
import csv

# Add resources
for resource in ["food", "clothing", "language", "legal services", "transportation", "medical care", "education and enrollment", "religious services", "counseling", "housing"]:
	r = Resource(name=resource)
	r.save()

# Load user
aliya = User.objects.filter(username="aliya").first()

# Add providers
with open('providers.csv', 'rb') as csvfile:
	providers = csv.reader(csvfile, delimiter=',', quotechar='"')
	name=""
	for index, row in enumerate(providers):
		if index >0:
			p = Provider(admin = aliya, name = row[0], logo=row[2], URL=row[3])
			if row[0] != name:
				p.save()
				name=row[0]

with open('providers.csv', 'rb') as csvfile:
	providers = csv.reader(csvfile, delimiter=',', quotechar='"')
	for index, row in enumerate(providers):
		if index >0:
			p = Provider.objects.filter(name=row[0]).first()
			l= Location(POC_firstname = "Aliya", POC_firstname2="", POC_lastname="", POC_lastname2="", provider = p, address = (str(row[1])+str(row[5])+str(row[6])+str(row[7])+str(row[8])), latitude=0.00, longitude=0.00, phone = row[10], is_headquarters=True, hours_open=row[11])
			l.save()

with open('providers.csv', 'rb') as csvfile:
	providers = csv.reader(csvfile, delimiter=',', quotechar='"')
	for index, row in enumerate(providers):
		if index >0:
			p = Provider.objects.filter(name=row[0]).first()
			l= Location.objects.filter(provider=p).first()
			food = Resource.objects.filter(name="food").first()
			clothing = Resource.objects.filter(name="clothing").first()
			language = Resource.objects.filter(name="language").first()
			legal = Resource.objects.filter(name="legal services").first()
			transportation = Resource.objects.filter(name="transportation").first()
			medical = Resource.objects.filter(name="medical care").first()
			school = Resource.objects.filter(name="education and enrollment").first()
			counseling = Resource.objects.filter(name="counseling").first()
			housing = Resource.objects.filter(name="housing").first()
			if row[12] =='yes' or row[12]=='Yes':
				l.resources_needed.add(food)
				l.resources_available.add(food)
			if row[13] =='yes' or row[13]=='Yes':
				l.resources_needed.add(clothing)
				l.resources_available.add(clothing)
			if row[14] =='yes' or row[14]=='Yes':
				l.resources_needed.add(legal)
				l.resources_available.add(legal)
			if row[15] =='yes' or row[15]=='Yes':
				l.resources_needed.add(language)
				l.resources_available.add(language)
			if row[16] =='yes' or row[16]=='Yes':
				l.resources_needed.add(medical)
				l.resources_available.add(medical)
			if row[17] =='yes' or row[17]=='Yes':
				l.resources_needed.add(school)
				l.resources_available.add(school)
			if row[18] =='yes' or row[18]=='Yes':
				l.resources_needed.add(school)
				l.resources_available.add(school)
			if row[19] =='yes' or row[19]=='Yes':
				l.resources_needed.add(transportation)
				l.resources_available.add(transportation)
			if row[20] =='yes' or row[20]=='Yes':
				l.resources_needed.add(counseling)
				l.resources_available.add(counseling)
			if row[21] =='yes' or row[21]=='Yes':
				l.resources_needed.add(housing)
				l.resources_available.add(housing)
			l.save()
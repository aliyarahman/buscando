from django.contrib.auth.models import User
from app.views import Resource, Provider, Location
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
	for row in providers:
		p = Provider(admin = aliya, name = row[0], logo=row[2], URL=row[3])
		if row[0] != name:
			p.save()
			name=row[0]
	for row in providers:
		p = Provider.objects.filter(name=row[0]).first()
		l= Location(POC_firstname = "Aliya", POC_firstname2="", POC_lastname="", POC_lastname2="", provider = p, address = (str(row[1])+str(row[5])+str(row[6])+str(row[7])+str(row[8])), latitude=0.00, longitude=0.00, phone = row[10], is_headquarters=True, hours_open=row[11])
		l.save()

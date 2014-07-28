from django.contrib.auth.models import User
from app.views import Resource, Provider, Location
import csv

# Add resources
for resource in ["food", "clothing", "legal services", "transportation", "medical care", "education and enrollment", "religious services", "counseling", "housing"]:
	r = Resource(name=resource)
	r.save()

# Load user
users = User.objects.all()
aliya = users[0]

# Add providers
with open('providers.csv', 'rb') as csvfile:
	providers = csv.reader(csvfile, delimiter=',', quotechar='"')
	for row in providers:
		p = Provider(admin = aliya, admin_firstname2 = "", admin_lastname2="", name = row[0], logo=row[2], URL=row[3], approved = False)
		#Commit it
		p.save()
		# Add locations
		for row in providers:
			l= Location(POC_firstname = "Aliya", POC_firstname2="", POC_lastname="", POC_lastname2="", provider = p, address = (str(row[1])+str(row[5])+str(row[6])+str(row[7])+str(row[8])), latitude=0.00, longitude=0.00, phone = row[10], is_headquarters=True, hours_open=row[11])
			# Commit
			l.save()
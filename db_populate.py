from django.contrib.auth.models import User
from app.models import Role
from app.views import *
import csv
import os
from django.db.utils import IntegrityError

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "buscando.settings")

# Add resources
for resource in ["food", "clothing", "language", "legal services", "transportation", "medical care", "education and enrollment", "religious services", "counseling", "housing"]:
    if len(Resource.objects.filter(name=resource)) == 0:
        r = Resource(name=resource)
        r.save()

# Add roles
for role, access in [('Volunteer', 1), ('Organization Staff', 2), ('Task Force Staff', 3), \
	('Buscando Staff', 90)]:
	r = Role(**{
			'name': role,
			'access_level': access
		})
	r.save()

# Load user


try:
	fake_user = User.objects.create_user(username="test_user", email = 		"test_user_email", password = "test_password", first_name = "test_first_name", 		last_name = "test_last_name")
	fake_user.save()
except IntegrityError:
	pass

user = User.objects.filter(username="test_user").first()

# Add providers
# to make things easier on the partner orgs, we let them enter a line for each of their locations. We will deal with separating the provider (name, logo, url) and the location (specific information about the location, hours, lat/log, etc). We need to dedup for provider names, but then load each location, so we'll loop through this file twice.
with open('providers.csv', 'rb') as csvfile:
	providers = csv.reader(csvfile, delimiter=',', quotechar='"')

	for index, row in enumerate(providers):
		if index >0:

			if len(Provider.objects.filter(name=row[0])) == 0:
				p = Provider(admin = user, name = row[0], logo=row[2], URL=row[3])

				p.save()

# Add locations
with open('providers.csv', 'rb') as csvfile:
	providers = csv.reader(csvfile, delimiter=',', quotechar='"')
	for index, row in enumerate(providers):
		if index >0:
			p = Provider.objects.filter(name=row[0]).first()
			l= Location(POC_firstname = "Aliya", POC_firstname2="", POC_lastname="", POC_lastname2="", provider = p, address = (str(row[1])+str(row[5])+str(row[6])+str(row[7])+str(row[8])), latitude=0.00, longitude=0.00, phone = row[10], is_headquarters=True, hours_open=row[11])
			l.save()

# Add relationships
with open('providers.csv', 'rb') as csvfile:
	providers = csv.reader(csvfile, delimiter=',', quotechar='"')
	for index, row in enumerate(providers):
		if index >0:
            
            #broken below: we need to get all locations for a provider and get the appropriate resources. below is just getting resources for the first location for each provider.
			p = Provider.objects.filter(name=row[0]).first()
			provider_locations = Location.objects.filter(provider=p)
            
            
            
			food = Resource.objects.filter(name="food").first()
			clothing = Resource.objects.filter(name="clothing").first()
			language = Resource.objects.filter(name="language").first()
			legal = Resource.objects.filter(name="legal services").first()
			transportation = Resource.objects.filter(name="transportation").first()
			medical = Resource.objects.filter(name="medical care").first()
			school = Resource.objects.filter(name="education and enrollment").first()
			counseling = Resource.objects.filter(name="counseling").first()
			housing = Resource.objects.filter(name="housing").first()
            
            #fix below to deal with case and whitespace
			for l in provider_locations:
				if row[12].lower().strip() =='yes':
					l.resources_needed.add(food)
					l.resources_available.add(food)
				if row[13].lower().strip() =='yes':
					l.resources_needed.add(clothing)
					l.resources_available.add(clothing)
				if row[14].lower().strip() =='yes':
					l.resources_needed.add(legal)
					l.resources_available.add(legal)
				if row[15].lower().strip() =='yes':
					l.resources_needed.add(language)
					l.resources_available.add(language)
				if row[16].lower().strip() =='yes':
					l.resources_needed.add(medical)
					l.resources_available.add(medical)
				if row[17].lower().strip() =='yes':
					l.resources_needed.add(school)
					l.resources_available.add(school)
				if row[18].lower().strip() =='yes':
					l.resources_needed.add(school)
					l.resources_available.add(school)
				if row[19].lower().strip() =='yes':
					l.resources_needed.add(transportation)
					l.resources_available.add(transportation)
				if row[20].lower().strip() =='yes':
					l.resources_needed.add(counseling)
					l.resources_available.add(counseling)
				if row[21].lower().strip() =='yes':
					l.resources_needed.add(housing)
					l.resources_available.add(housing)
				l.save()
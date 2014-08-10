from django.contrib.auth.models import User
#from app.models import Role
from app.views import *
import csv
import os
from django.db.utils import IntegrityError

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "buscando.settings")
#Rachel and Shannon had a really tough time figuring out exactly how to
#get DJANGO_SETTINGS_MODULE set properly, and eventually Rachel just ran
#export DJANGO_SETTINGS_MODULE=buscando.settings
#from the command line which worked (on a mac, at least) and made this scrip runable
#I'm not really sure if the above line is doing anything anymore.


# Add resources
for resource in ["food", "clothing", "language", "legal services", "transportation", "medical care", "education and enrollment", "religious services", "counseling", "housing", "recreation", "volunteers", "other"]:
    if len(Resource.objects.filter(name=resource)) == 0:
        r = Resource(name=resource)
        r.save()

# Add roles
""""
for role, access in [('Volunteer', 1), ('Organization Staff', 2), ('Task Force Staff', 3), \
	('Buscando Staff', 90)]:
	r = Role(**{
			'name': role,
			'access_level': access
		})
	r.save()
"""
# Load user

#try/except to prevent erroring out if the dummy user already exists
try:
	fake_user = User.objects.create_user(username="test_user", email = 		"test_user_email", password = "test_password", first_name = "test_first_name", 		last_name = "test_last_name")
	fake_user.save()
except IntegrityError:
	pass


user = User.objects.filter(username="test_user").first()

# Add providers
# to make things easier on the partner orgs, we let them enter a line for each of their locations. We will deal with separating the provider (name, logo, url) and the location (specific information about the location, hours, lat/log, etc). We need to dedup for provider names, but then load each location, so we'll loop through this file twice.


#expecting CSV with the following headers:
#provider_name,location_name,image,website,address1,address2,city,state,zip,contact,phone_contact,hours,food,clothing,legal,language,medical,school,school2,transportation,counseling,housing

with open('providers.csv', 'rb') as csvfile:
	providers = csv.DictReader(csvfile, delimiter=',', quotechar='"')
	provider_names = [p.name.strip().lower() for p in Provider.object.all()]#creating a list for searching to dedup provider names
		#creating this list is probably not the fastest, but allows us to dedup easily based on caps/spacing without losing that formatting
		#in the name that goes into the database. this list ensures deduping against what's currently in the DB as well

	for index, row in enumerate(providers):
		if index >0:
			provider_name = row['provider_name']

			if provider_name.strip().lower() not in provider_names:
				p = Provider(admin = user, name = provider_name.strip(), logo=row['image'].strip(), URL=row['website'].strip())
				provider_names.append(provider_name.strip().lower())

				p.save()

# Add locations
with open('providers.csv', 'rb') as csvfile:
	providers = csv.DictReader(csvfile, delimiter=',', quotechar='"')
	for index, row in enumerate(providers):
		if index >0:
			p = Provider.objects.filter(name=row['provider_name']).first()
			address_fields = [row['location_name'],row['address1'],row['address2'],row['city'],row['state'],row['zipcode']]
			address = ' '.join(filter(None,[str(a.strip()) for a in address_fields])) #ensures blank fields and extra whitespace won't mess up formatting
			
			l= Location(POC_firstname = "Aliya", POC_firstname2="", POC_lastname="", POC_lastname2="", provider = p, address = address, latitude=0.00, longitude=0.00, phone = row['phone'].strip(), is_headquarters=True, hours_open=row['hours'].strip())
			l.save()

# Add relationships
with open('providers.csv', 'rb') as csvfile:
	providers = csv.DictReader(csvfile, delimiter=',', quotechar='"')
	for index, row in enumerate(providers):
		if index >0:
            

			p = Provider.objects.filter(name=row['provider_name'].strip()).first()
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
            

			for l in provider_locations:
				if row['food'].lower().strip() =='yes':
					l.resources_needed.add(food)
					l.resources_available.add(food)
				if row['clothing'].lower().strip() =='yes':
					l.resources_needed.add(clothing)
					l.resources_available.add(clothing)
				if row['legal'].lower().strip() =='yes':
					l.resources_needed.add(legal)
					l.resources_available.add(legal)
				if row['language'].lower().strip() =='yes':
					l.resources_needed.add(language)
					l.resources_available.add(language)
				if row['medical'].lower().strip() =='yes':
					l.resources_needed.add(medical)
					l.resources_available.add(medical)
				if row['school'].lower().strip() =='yes':
					l.resources_needed.add(school)
					l.resources_available.add(school)
				if row['transportation'].lower().strip() =='yes':
					l.resources_needed.add(transportation)
					l.resources_available.add(transportation)
				if row['counseling'].lower().strip() =='yes':
					l.resources_needed.add(counseling)
					l.resources_available.add(counseling)
				if row['housing'].lower().strip() =='yes':
					l.resources_needed.add(housing)
					l.resources_available.add(housing)
				l.save()

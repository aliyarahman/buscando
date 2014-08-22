from django.contrib.auth.models import User
#from app.models import Role
from app.views import *
import csv
import os
from django.db.utils import IntegrityError
import time


#notes about deduping:
#Providers: This script will not add a provider if one with the same name already exists.
	#names are stripped of leading/trailing spaces and case before checking
	#but we do not check for spelling errors
	
#Locations: This script will not add a location if a location with the same provider
	#and address exists.
	
#Resources: This script NOT add any resources to a location that already exist
	#because it may have been carefully and lovingly hand-edited




os.environ.setdefault("DJANGO_SETTINGS_MODULE", "buscando.settings")
#Rachel and Shannon had a really tough time figuring out exactly how to
#get DJANGO_SETTINGS_MODULE set properly, and eventually Rachel just ran
#export DJANGO_SETTINGS_MODULE=buscando.settings
#from the command line which worked (on a mac, at least) and made this scrip runable
#I'm not really sure if the above line is doing anything anymore.


csv_name = 'providers_from_md211.csv'

# Add resources

#resources in this list need to match the CSV headers AND the resources names in the app.
resource_types = ["food", "clothing", "language", "legal services", "transportation", "medical care", "education and enrollment", "religious services", "counseling", "housing", "recreation", "volunteers", "other"]


for resource in resource_types:
    if len(Resource.objects.filter(name=resource)) == 0:
        r = Resource(name=resource)
        r.save()


resource_objects = [Resource.objects.filter(name=r).first() for r in resource_types]

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




with open(csv_name, 'rb') as csvfile:
	providers = csv.DictReader(csvfile, delimiter=',', quotechar='"')
	

	for index, row in enumerate(providers):
		
		provider_name = row['provider_name'].strip()
		
		existing_provider = Provider.objects.filter(name__iexact = provider_name.strip())
		
		if len(existing_provider) == 0:
			p = Provider(admin = user, name = provider_name.strip(), logo=row['image'].strip(), URL=row['website'].strip())


			p.save()
		else:
			p = existing_provider.first()

		# Add locations

		address_fields = [row['location_name'],row['address1'],row['address2'],row['city'],row['state'],row['zipcode']]
		address = ' '.join(filter(None,[str(a.strip()) for a in address_fields])) #ensures blank fields and extra whitespace won't mess up formatting


		

		
		l= Location(POC_firstname = "Aliya", POC_firstname2="", POC_lastname="", POC_lastname2="", provider = p, address = address, latitude=0.00, longitude=0.00, phone = row['phone'].strip()[0:20], is_headquarters=True, hours_open=row['hours'].strip())
		l.save()
		time.sleep(.1)
		
		if len(Location.objects.filter(provider=p).filter(address=l.address)) > 1:
			l.delete() #need to save and then delete because the address gets geocoded and thus changed
				#so this is the only way to get at the geocoded address
        

        

		else:
			for r in resource_objects:
				if row[r.name].lower().strip() == 'yes':
					l.resources_needed.add(r)
					l.resources_available.add(r)
		
		
		
		

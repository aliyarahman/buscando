from django.db import models
from django.contrib.auth.models import User
from geopy.geocoders import GoogleV3
from django.utils.translation import ugettext as _

import datetime



class Provider(models.Model):
	admin = models.ForeignKey(User) # This is what I just typed
	admin_firstname2 = models.CharField(max_length=45, null=True, blank=True)
	admin_lastname2 = models.CharField(max_length=45, null=True, blank=True)
	name = models.CharField(max_length=140)
	logo = models.CharField(max_length=140, null=True, blank = True)
	URL = models.CharField(max_length=140)
	approved = models.BooleanField(default = True) # Change this in production
	preferred = models.BooleanField(default = False)

	# Auto-generated timestamps
	created_at = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now())
	updated_at = models.DateTimeField(auto_now=True, default=datetime.datetime.now())

	def __unicode__(self):
		return self.name

class Resource(models.Model):
	name = models.CharField(max_length=30, unique=True)
	details = models.CharField(max_length=255, null = True, blank = True)

	def __unicode__(self):
		return self.name



class Location(models.Model):
	POC_firstname = models.CharField(max_length=45)
	POC_firstname2 = models.CharField(max_length=45, null=True, blank=True)
	POC_lastname = models.CharField(max_length=45)
	POC_lastname2 = models.CharField(max_length=45, null=True, blank=True)
	provider = models.ForeignKey(Provider)
	address = models.CharField(max_length=140)
	latitude = models.FloatField(default=0, null=True, blank=True)
	longitude = models.FloatField(default=0, null=True, blank=True)
	phone = models.CharField(max_length=20)
	is_headquarters = models.BooleanField(default=False)
	hours_open = models.CharField(max_length=200)
	resources_needed = models.ManyToManyField(Resource, related_name="resources_needed", null=True, blank=True)
	resources_available = models.ManyToManyField(Resource, related_name="resources_available", null=True, blank=True)

	# Auto-generated timestamps
	created_at = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now())
	updated_at = models.DateTimeField(auto_now=True, default=datetime.datetime.now())

	def __unicode__(self):
		return self.address

	def save(self):
		if self.latitude is None or self.longitude is None or int(self.latitude) == 0 or int(self.longitude) == 0:
			try:
				geolocator = GoogleV3()
				self.address, (self.latitude, self.longitude) = geolocator.geocode(self.address)
			except:
				self.latitude = 0
				self.longitude = 0
		super(Location, self).save()



class Volunteer(models.Model):
	first_name = models.CharField(max_length=15)
	last_name = models.CharField(max_length=15)
	email = models.EmailField(max_length=255)
	phone = models.CharField(max_length=15)
	address = models.CharField(max_length=255)
	has_resources = models.ManyToManyField(Resource, related_name="has_resources", null=True, blank=True)

	created_at = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now())
	updated_at = models.DateTimeField(auto_now=True, default=datetime.datetime.now())

	def __unicode__(self):
 		return self.email



class ZipcodeCoordinates(models.Model):

	" Storing this so multiple searches to a single zip code only retrieve coordinates once. "

	zipcode = models.CharField(max_length=10)
	latitude = models.FloatField(default=0)
	longitude = models.FloatField(default=0)

	def save(self):
		if self.latitude == 0 or self.longitude == 0:
			try:
				geolocator = GoogleV3()
				address, (self.latitude, self.longitude) = geolocator.geocode(self.zipcode)
			except:
				pass
		super(ZipcodeCoordinates, self).save()

	def __unicode__(self):
		return '{0} ({1}, {2})'.format(self.zipcode, self.latitude, self.longitude)

class Search(models.Model):

	"One search for resources near a location."

	location = models.CharField(max_length=255)
	resource = models.CharField(max_length=255)

	# Auto-generated timestamps
	created_at = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now())
	updated_at = models.DateTimeField(auto_now=True, default=datetime.datetime.now())

	def __unicode__(self):
		return '{0}: {1} ({2})'.format(self.location, self.resource, self.created_at)

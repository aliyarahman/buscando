from django.db import models
from django.contrib.auth.models import User
#from django.contrib.auth.models import AbstractBaseUser

from geopy.geocoders import GoogleV3

import datetime

class Role(models.Model):
	name = models.CharField(max_length=255)
	access_level = models.IntegerField(default=0)

	def __unicode__(self):
		return '{0} (Access level {1})'.format(self.name, self.access_level)

# class User is built in to Django: has firsrtname, lastname, username, email, password
# That User is referenced via foreign key to attach to the Provider profile

class User(AbstractBaseUser):
	"""
	Custom user class to include firstname2 and lastname2.
	"""
	firstname2 = models.CharField(max_length=45, null=True, blank=True)
	lastname2 = models.CharField(max_length=45, null=True, blank=True)
	role = models.ForeignKey(Role, related_name='user')

class Provider(models.Model):
	admin = models.ForeignKey(User) # This is what I just typed
	admin_firstname2 = models.CharField(max_length=45, null=True, blank=True)
	admin_lastname2 = models.CharField(max_length=45, null=True, blank=True)
	name = models.CharField(max_length=140)
	logo = models.CharField(max_length=140)
	URL = models.CharField(max_length=140)
	approved = models.BooleanField(default = True) # Change this in production

	# Auto-generated timestamps
	created_at = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now())
	updated_at = models.DateTimeField(auto_now=True, default=datetime.datetime.now())

	def __unicode__(self):
		return self.name

class Resource(models.Model):
	name = models.CharField(max_length=30, unique=True)

	def __unicode__(self):
		return self.name

class Location(models.Model):
	POC_firstname = models.CharField(max_length=45)
	POC_firstname2 = models.CharField(max_length=45, null=True, blank=True)
	POC_lastname = models.CharField(max_length=45)
	POC_lastname2 = models.CharField(max_length=45, null=True, blank=True)
	provider = models.ForeignKey(Provider)
	address = models.CharField(max_length=140)
	latitude = models.FloatField(default=0)
	longitude = models.FloatField(default=0)
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
		if self.latitude == 0 or self.longitude == 0:
			try:
				geolocator = GoogleV3()
				self.address, (self.latitude, self.longitude) = geolocator.geocode(self.address)
			except:
				pass
		super(Location, self).save()

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

from django.db import models
from django.contrib.auth.models import User

from geopy.geocoders import GoogleV3
import datetime

# class User is built in to Django: has firsrtname, lastname, username, email, password
# That User is referenced via foreign key to attach to the Provider profile

class Provider(models.Model):
	admin = models.ForeignKey(User) # This is what I just typed
	admin_firstname2 = models.CharField(max_length=45, null=True, blank=True)
	admin_lastname2 = models.CharField(max_length=45, null=True, blank=True)
	name = models.CharField(max_length=140, unique=True)
	logo = models.CharField(max_length=45)
	URL = models.CharField(max_length=45)
	approved = models.BooleanField(default = False)

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
	resources_needed = models.ManyToManyField(Resource, related_name="resources_needed")
	resources_available = models.ManyToManyField(Resource, related_name="resources_available")

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
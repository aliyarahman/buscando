from django.db import models
from django.contrib.auth.models import User


# class User is built in to Django: has firsrtname, lastname, username, email, password
# That User is referenced via foreign key to attach to the Provider profile

class Provider(models.Model):
	admin = models.ForeignKey(User) # This is what I just typed
	admin firstname2 = models.CharField(max_length=45, default = "")
	admin_lastname2 = models.CharField(max_length=45, default = "")		
	name = models.CharField(max_length=140, unique = True)
	logo = models.CharField(max_length=45)
	URL = models.CharField(max_length=45)
	
	def __unicode__(self):
		return self.name


class Location(models.Model):
	POC_firstname = models.CharField(max_length=45)
	POC firstname2 = models.CharField(max_length=45, default = "")
	POC_lastname = models.CharField(max_length=45)
	POC_last2name = models.CharField(max_length=45, default="")
	provider = models.ForeignKey(Provider)
	address = models.CharField(max_length=140)
	phone = models.CharField(max_length=20)
	is_headquarters = models.BooleanField
	hours_open = models.CharField(max_length=200)
    resources_needed = models.ManyToManyField(Resource, related_name="resources_needed")
    resources_available = models.ManyToManyField(Resource, related_name="resources_available")
    

class Resource(models.Model):
	name = models.CharField(max_length=30, unique = True)
	locations = models.ManyToManyField(Provider, default = [])

	def __unicode__(self):
		return self.name
		

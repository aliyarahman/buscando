from django.db import models
from django.contrib.auth.models import User

class Provider(models.Model):
	name = models.CharField(max_length=140, unique = True)
	city = models.CharField(max_length=45)

	def __unicode__(self):
		return self.name


class Resource(models.Model):
	name = models.CharField(max_length=30, unique = True)
	providers = models.ManyToManyField(Provider, default = [])

	def __unicode__(self):
		return self.name



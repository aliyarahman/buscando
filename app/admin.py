from django.contrib import admin
from app.models import Provider, Resource, Location

# Register your models here.
admin.site.register(Provider)
admin.site.register(Location)
admin.site.register(Resource)
from django.contrib import admin
from app.models import Provider, Resource, Location, Volunteer

class LocationInline(admin.StackedInline):
    model = Location
    extra = 1

class ProviderAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'logo', 'URL']}),
        ('Admin information', {'fields': ['admin', 'admin_firstname2', 'admin_lastname2']}),]
    inlines = [LocationInline]

# Register your models here.
admin.site.register(Provider)
admin.site.register(Location)
admin.site.register(Resource)
admin.site.register(Volunteer)

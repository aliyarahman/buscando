from django import forms
from app.models import Provider, Resource, Location
from django.forms import ModelForm
from django.forms.models import modelformset_factory

class LocationForm(ModelForm):
	class Meta:
		model = Location
		fields = (
			'POC_firstname',
			'POC_firstname2',
			'POC_lastname',
			'POC_lastname2',
			'address',
			'latitude',
			'longitude',
			'phone',
			'is_headquarters',
			'hours_open',
			'resources_needed',
			'resources_available',
			)

class ProviderForm(ModelForm):
	class Meta:
		model = Provider
		fields = ('admin_firstname2', 'admin_lastname2', 'name', 'logo', 'URL', )

	# def is_valid(self):
	# 	result = super(ProviderForm, self).is_valid()

	# 	if hasattr(self.form, 'nested'):
	# 		for location_form in form.nested

	def add_fields (self, form, index):

		# create the Provider fields
		super(ProviderForm, self).add_fields(form, index)

		# create the Location formset
		try:
			instance = self.get_queryset()[index]
			pk_value = instance.pk
		except IndexError:
			instance=None
			pk_value = hash(form.prefix)

		# store formset in the .nested property
		form.nested = [
			LocationFormset( 
								instance = instance,
								queryset = Location.objects.filter(provider = pk_value) ,
								prefix = 'locations_%s' % pk_value ,
							)
						]

LocationFormset = modelformset_factory(Location, extra=1)
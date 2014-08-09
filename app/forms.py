from django import forms
from app.models import Provider, Resource, Location
from django.forms import ModelForm
from django.forms.models import modelformset_factory

class ResourcesChoiceField(forms.ModelMultipleChoiceField):
	def label_from_instance(self, obj):
	    return obj.name    

class LocationForm(ModelForm):
	resources_needed = ResourcesChoiceField(
							queryset = Resource.objects, 
							widget=forms.CheckboxSelectMultiple(),
							required=False,
							)
	resources_available = ResourcesChoiceField(
							queryset = Resource.objects, 
							widget=forms.CheckboxSelectMultiple(),
							required=False,
							)

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

	# def __init__(self, *args, **kwargs):
	# 	super(LocationForm, self).__init__(*args,**kwards)
	# 	self.fields['POC_firstname'].widget = TextInput(attrs={
	# 		'class': ''
	# 		})

class ProviderForm(ModelForm):
	class Meta:
		model = Provider
		fields = ('name', 'logo', 'URL', )

LocationFormset = modelformset_factory(Location, extra=1)
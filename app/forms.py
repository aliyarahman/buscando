from django import forms
from app.models import Provider, Resource, Location
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from django.forms.models import modelformset_factory



VOLUNTEER_CHOICES = (('food', _('Food')),
                     ('clothing', _('Clothing')),
                     ('language', _('English-Spanish translation')),
                     ('legal services', _('Legal services')),
                     ('transportation', _('Transportation')),	
                     ('medical care', _('Medical care')),
                     ('education and enrollment', _('Help with education and enrollment')),
                     ('religious services', _('Religious services')),
                     ('counseling', _('Mental health and counseling')),
                     ('recreation', _('Recreation')),
                     ('volunteers', _('Volunteer recruitment')),
                     ('other', _('Other')),)

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


class ProviderForm(ModelForm):
	class Meta:
		model = Provider
		fields = ('name', 'URL',)

LocationFormset = modelformset_factory(Location, extra=1)


class UserForm(forms.Form):
	first_name = forms.CharField(max_length=45)
	last_name = forms.CharField(max_length=45)
	email = forms.CharField(max_length=45)	
	has_resources = forms.MultipleChoiceField(
							choices = VOLUNTEER_CHOICES,
							widget=forms.CheckboxSelectMultiple(),
							required=True,
							)
	other = forms.CharField(max_length = 45, required=False)
	phone = forms.CharField(max_length=15)
	address = forms.CharField(max_length=255)

from django import forms
from app.models import Provider, Resource, Location
from django.forms import ModelForm
from django.forms.models import inlineformset_factory

class ProviderForm(ModelForm):
	class Meta:
		model = Provider
		fields = ('admin', 'admin_firstname2', 'admin_lastname2', 'name', 'logo', 'URL', )

LocationFormset = inlineformset_factory(Provider, Location, extra=1)
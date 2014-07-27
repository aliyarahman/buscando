from django import forms
from app.models import Provider, Resource, Location
from django.forms import ModelForm
from django.forms.models import inlineformset_factory

class ProviderForm(ModelForm):
	class Meta:
		model = Provider
		fields = ('admin', 'name', 'URL', 'logo')

LocationFormset = inlineformset_factory(Provider, Location, extra=1)
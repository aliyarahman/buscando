import urlparse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from app.models import Provider, Resource, Location
from app.forms import ProviderForm, LocationFormset

def index(request):
	return render(request, "index.html")

def about(request):
	return render(request, "about.html")

def resources(request):
	return render(request, "resources.html")

def organization_register(request):
	return render(request, "organization_register.html")


@login_required
def profile(request):
#	provider = get_object_or_404(City, pk=provider_id)
	return render(request, "profile.html")
#	return render(request, "profile.html", {'provider': provider })

def add_provider(request):
	if request.method == "POST":
		form = ProviderForm(request.POST)
		if form.is_valid():
			provider = form.save(commit=False) # changed from save to save nested locations
			# timestamp?
			provider.save()
			return HttpResponseRedirect(reverse('provider_detail', kwargs={'provider_id': provider.id}))
	else: # request.method == "GET"
		form = ProviderForm()

	return render(request, "provider/new.html", { 'form': form })

def edit_provider(request, provider_id):
	provider = get_object_or_404(Provider, id=provider_id)

	if request.method == 'POST':
		form = ProviderForm(request.POST, instance=provider)

		if form.is_valid():
			provider = form.save(commit=False)
			# timestamp?
			provider.save()
			return HttpResponseRedirect(reverse('provider_detail', kwargs={'provider_id': provider.id}))

	else:
		form = ProviderForm(instance=provider)

	return render(request, "provider/edit.html", { 'form': form })

def provider_detail(request, provider_id):
	try:
		provider = Provider.objects.get(pk=provider_id)
	except Provider.DoesNotExist:
    	# If no Provider has id provider_id, we raise an HTTP 404 error.
		raise Http404
	return render(request, 'provider/detail.html', {'provider': provider})
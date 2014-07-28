import urlparse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from app.models import Provider, Resource, Location, Search, ZipcodeCoordinates
from app.forms import ProviderForm, LocationFormset
from geopy.distance import vincenty

RADIUS_DISTANCE = 35 # miles

def index(request):
	return render(request, "index.html")

def about(request):
	return render(request, "about.html")

def organization_register(request):
	return render(request, "organization_register.html")

def resources(request):

    zipcode = request.POST.get('zipcode')
    resource = request.POST.get('resource')

    if not zipcode and not resource:
        return render(request, 'resources.html')

    if zipcode and resource:
        # Save the search
        search = Search(**{
                'zipcode': zipcode,
                'resource': resource
            })
        search.save()

    try:
        zipcode = int(zipcode[:5])

        # Zero-pad New England zipcodes
        if len(str(zipcode)) == 4:
            zipcode = '0{0}'.format(zipcode)
    except:
        messages.error(request, "Sorry, I didn't recognize that zipcode. Please try again.")
        return HttpResponseRedirect('/app')
    else:
        try:
            zipcode_coords = ZipcodeCoordinates.objects.get(zipcode=zipcode)
        except:
            # If this zipcode has not yet been searched, create a new one
            zipcode_coords = ZipcodeCoordinates(zipcode=zipcode)
            zipcode_coords.save()

    try:
        resource = Resource.objects.get(name=resource.lower())
    except:
        messages.error(request, "Please choose a resource and try again.")
        return HttpResponseRedirect('/app')
    else:
        locations = Location.objects.select_related('provider').filter(
            resources_available=resource).exclude(provider__approved=False)
        within_radius = []
        for location in locations:
            if vincenty(
                (location.latitude, location.longitude), 
                (zipcode_coords.latitude, zipcode_coords.longitude)
            ).miles <= RADIUS_DISTANCE:
                within_radius.append(location)

    context = {
        'within_radius': within_radius,
        'zipcode': zipcode,
        'resource': resource
    }

    return render(request, 'resources.html', dictionary=context)

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
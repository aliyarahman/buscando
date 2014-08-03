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
from app.forms import ProviderForm, LocationFormset, LocationForm
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
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
        'resource': resource,
        'search_from': zipcode_coords,
    }

    return render(request, 'resources.html', dictionary=context)

@login_required
def profile(request):
#	provider = get_object_or_404(City, pk=provider_id)
	return render(request, "profile.html")
#	return render(request, "profile.html", {'provider': provider })

def organization_home(request):
	orgs = Provider.objects.filter(admin_id = request.user.id)
	if orgs:
		# If an organization is logged in, bring them to their profile
		provider = orgs[0]
		return HttpResponseRedirect(reverse('provider_detail', kwargs={'provider_id': provider.id}))
	else:
		# This user is not associated with an organization.
		# Should this be a login page for organizations?
		# Or just an index of all organizations (with a search sidebar)?
		return HttpResponseRedirect(reverse('organization_home'))

def login_page(request):
	if request.method == "POST":
		form = AuthenticationForm(data=request.POST)
		if form.is_valid():
			login(request, form.get_user())
			return HttpResponseRedirect(reverse('organization_home'))
	else:
		form = AuthenticationForm()
		
	return render(request, 'login.html', {'form': form})

def logout_page(request):
	logout(request)
	return HttpResponseRedirect(reverse('index'))

def add_provider(request):
	if request.method == "POST":
		admin_form = UserCreationForm(request.POST)
		provider_form = ProviderForm(request.POST)
		location_form = LocationForm(request.POST)

		if admin_form.is_valid() and provider_form.is_valid() and location_form.is_valid():
			admin = admin_form.save()
			provider = provider_form.save(commit=False)
			provider.admin = admin
			provider.save()
			location = location_form.save(commit=False)
			location.provider = provider
			location.save()
			location_form.save_m2m()
			return HttpResponseRedirect(reverse('provider_detail', kwargs={'provider_id': provider.id}))

	else:
		admin_form = UserCreationForm()
		provider_form = ProviderForm()
		location_form = LocationForm()

	return render(request, "provider/new.html", { 
												'provider_form': provider_form, 
												'location_form': location_form,
												'admin_form': admin_form,
												 })

@login_required
def edit_provider(request, provider_id):

	provider = get_object_or_404(Provider, id=provider_id)
	admin_user = provider.admin

	#TEMPORARY
	location = Location.objects.filter(provider__pk = provider_id)[0]

	if request.user == admin_user: # only the provider's registered user can edit page

		if request.method == 'POST':
			provider_form = ProviderForm(request.POST,instance=provider)
			location_form = LocationForm(request.POST,instance=location)

			if provider_form.is_valid() and location_form.is_valid():
				provider = provider_form.save(commit=False)
				provider.admin = admin_user
				provider.save()
				location = location_form.save(commit=False)
				location.provider = provider
				location.save()
				location_form.save_m2m()
				return HttpResponseRedirect(reverse('provider_detail', kwargs={'provider_id': provider.id}))

		else:
			provider_form = ProviderForm(instance=provider)
			location_form = LocationForm(instance=location) #todo: turn into formsets--right now this is creating a new loca

		return render(request, "provider/edit.html", { 
												'provider_form': provider_form, 
												'location_form': location_form
												 })

	else:
		return HttpResponseRedirect(reverse('index'))

def provider_detail(request, provider_id):
	provider = get_object_or_404(Provider, id=provider_id)
	admin_user = provider.admin
	if request.user == admin_user: 
		can_edit = True
	else:
		can_edit = False
	locations = Location.objects.filter(provider__pk = provider_id)

	return render(request, 'provider/detail.html', {
													'provider': provider, 
													'locations': locations, 
													'can_edit': can_edit,
													})
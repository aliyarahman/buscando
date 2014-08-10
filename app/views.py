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
from app.forms import ProviderForm, LocationFormset, LocationForm, UserForm
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from geopy.distance import vincenty
from geopy.geocoders import GoogleV3
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
import requests

RADIUS_DISTANCE = 35 # miles

def index(request):
	return render(request, "index.html")

def about(request):
	return render(request, "about.html")

def resources(request):
    searched_location = request.POST.get('location')
    resource = request.POST.get('resource')

    if not searched_location and not resource:
        return render(request, 'resources.html')

    if searched_location and resource:
        # Save the search
        search = Search(**{
                'location': searched_location,
                'resource': resource
            })
        search.save()

    coords = False

    try:
        searched_location = int(searched_location[:5])

        # Zero-pad New England zipcodes
        if len(str(searched_location)) == 4:
            searched_location = '0{0}'.format(searched_location)
    except:
        try:
            geolocator = GoogleV3()
            address, (latitude, longitude) = geolocator.geocode(searched_location)
        except:
            pass
        else:
            coords = {
                'latitude': latitude,
                'longitude': longitude,
            }
    else:
        try:
            zipcode_coords = ZipcodeCoordinates.objects.get(zipcode=searched_location)
        except:
            # If this zipcode has not yet been searched, create a new one
            zipcode_coords = ZipcodeCoordinates(zipcode=searched_location)
            zipcode_coords.save()
        finally:
            coords = {
                'latitude': zipcode_coords.latitude,
                'longitude': zipcode_coords.longitude
            }

    if not coords:
        messages.error(request, "Sorry, I couldn't find that location. Please try again. You can also search by city or by zipcode.")
        return HttpResponseRedirect('/app/resources')

    try:
        resource = Resource.objects.get(name=resource.lower())
    except:
        messages.error(request, "Please choose a resource and try again.")
        return HttpResponseRedirect('/app/resources')
    else:
        locations = Location.objects.select_related('provider').filter(
            resources_available=resource).exclude(provider__approved=False)
        within_radius = []
        for location in locations:
            if vincenty(
                (location.latitude, location.longitude), 
                (coords['latitude'], coords['longitude'])
            ).miles <= RADIUS_DISTANCE:
                within_radius.append(location)

    context = {
        'within_radius': within_radius,
        'location': searched_location,
        'resource': resource,
        'search_from': coords,
    }

    print context

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

@login_required
def delete_provider(request, provider_id):
	provider = get_object_or_404(Provider, id=provider_id)
	admin_user = provider.admin
	if request.user == admin_user: # only the provider's registered user can delete
		provider.delete()
		admin_user.delete()
		return HttpResponseRedirect(reverse('index'))
	else:
		return HttpResponseRedirect(reverse('provider_detail', kwargs={'provider_id': provider.id}))

def add_provider(request):
	# users should only be able to make one provider
	if request.user.is_authenticated():
		return HttpResponseRedirect(reverse('index'))
	else:
		LocationFormset = modelformset_factory(Location, exclude=('provider',))
		if request.method == "POST":
			admin_form = UserCreationForm(request.POST)
			provider_form = ProviderForm(request.POST)
			location_formset = LocationFormset(request.POST, request.FILES)

			if admin_form.is_valid() and provider_form.is_valid() and location_formset.is_valid():
				u_name = admin_form.cleaned_data.get('username')
				u_pass = admin_form.cleaned_data.get('password2')
				admin = admin_form.save()
				provider = provider_form.save(commit=False)
				provider.admin = admin
				provider.save()
				for location_form in location_formset:
					location = location_form.save(commit=False)
					location.provider = provider
					location.save()
					location_form.save_m2m()
				location_formset.save()
				user = authenticate(username=u_name,
									password=u_pass)
				login(request, user)
				return HttpResponseRedirect(reverse('provider_detail', kwargs={'provider_id': provider.id}))

		else:
			admin_form = UserCreationForm()
			provider_form = ProviderForm()
			location_formset = LocationFormset(queryset=Location.objects.none())

		return render(request, "provider/new.html", { 
													'provider_form': provider_form, 
													'location_formset': location_formset,
													'admin_form': admin_form,
													 })

@login_required
def edit_provider(request, provider_id):

	provider = get_object_or_404(Provider, id=provider_id)
	admin_user = provider.admin

	if request.user == admin_user: # only the provider's registered user can edit page

		if request.method == 'POST':
			password_change_form = PasswordChangeForm(request.POST)
			provider_form = ProviderForm(request.POST,instance=provider)
			location_formset = LocationForm(request.POST,request.FILES)

			if password_change_form.is_valid() and provider_form.is_valid() and location_form.is_valid():
				password_change_form.save()
				provider = provider_form.save(commit=False)
				provider.admin = admin_user
				provider.save()
				for location_form in location_formset:
					location = location_form.save(commit=False)
					location.provider = provider
					#location.save()
					location_form.save_m2m()
				location_formset.save()
				return HttpResponseRedirect(reverse('provider_detail', kwargs={'provider_id': provider.id}))

		else:
			password_change_form = PasswordChangeForm(user=admin_user)
			provider_form = ProviderForm(instance=provider)
			location_formset = LocationFormset(queryset=Location.objects.filter(provider__pk = provider_id))

		return render(request, "provider/edit.html", { 
												'provider': provider,
												'provider_form': provider_form, 
												'location_formset': location_formset,
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



def add_volunteer(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect(reverse('index')) # Logged in users shouldn't be able to sign up
	else:
		if request.method == "POST":
			user_form = UserCreationForm(request.POST)
			profile_form = UserForm(request.POST)
			if user_form.is_valid() and profile_form.is_valid():
				u_name = user_form.cleaned_data.get('username')
				u_pass = user_form.cleaned_data.get('password2')
				user = user_form.save() # Save the basic user with email/username and password
				user.first_name = profile_form.cleaned_data.get("first_name")
				user.last_name = profile_form.cleaned_data.get("last_name")
				user.phone = profile_form.cleaned_data.get("phone")
				user.address = profile_form.cleaned_data.get("address")
				user.save()
				# Still need to add skills they have here
				user = authenticate(username=u_name,
									password=u_pass)
				login(request, user)
				return HttpResponseRedirect(reverse('resources'))
		else:
			user_form = UserCreationForm()
			profile_form = UserForm()
		return render(request, "volunteer/new.html", { 
													'user_form': user_form, 
													'profile_form': profile_form,
													 })

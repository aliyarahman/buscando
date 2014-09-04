import urlparse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from app.models import Provider, Resource, Location, Search, ZipcodeCoordinates, Volunteer
from app.forms import ProviderForm, LocationFormset, LocationForm, UserForm
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from geopy.distance import vincenty
from geopy.geocoders import GoogleV3
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from django.utils.translation import ugettext as _
import requests
from django.shortcuts import render_to_response
from django.utils import simplejson

RADIUS_DISTANCE = 35 # miles

def index(request):
	return render(request, "index.html")

def about(request):
	return render(request, "about.html")

def FAQ(request):
	return render(request, "FAQ.html")

def resources(request, **kwargs):
    searched_location = request.POST.get('location')
    resource = request.POST.getlist('resource')
    type_ = request.POST.get('type')
    radius = request.POST.get('radius')

    if not type_:
        type_ = request.GET.get('type')

    if not type_:
        type_ = kwargs.get('type')

    try:
        radius = int(radius)
        assert 10 < radius < 150
    except:
        radius = RADIUS_DISTANCE

    if not searched_location and not resource:
        return render(request, 'resources.html', { 'type': type_ })

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
        cdnt_find_loc_error_msg = _("Sorry, I couldn't find that location. Please try again. You can also search by city or by zipcode.")
        messages.error(request, cdnt_find_loc_error_msg)
        if type_:
            return HttpResponseRedirect(reverse('resources', kwargs={'type': type_}))
        else:
            return HttpResponseRedirect(reverse('resources'))

    try:
        if len(resource) == 1:
            resource = [Resource.objects.get(name=resource[0].lower())]
        elif len(resource) > 1:
            resource = Resource.objects.filter(name__in=[res.lower() for res in resource])
        else:
            raise ValueError
    except:
    	cdnt_find_res_error_msg = _("Please choose a resource and try again.")
        messages.error(request, cdnt_find_res_error_msg)
        if type_:
            return HttpResponseRedirect(reverse('resources', kwargs={'type': type_}))
        else:
            return HttpResponseRedirect(reverse('resources'))
    else:
        locations = Location.objects.select_related('provider').exclude(provider__approved=False)

        if len(resource) == 1: # Just one resource chosen
            locations = locations.filter(resources_available=resource[0])
        elif len(resource) > 1:
            locations = locations.filter(resources_available__in=resource)

        within_radius = []
        for location in locations:
            dist = vincenty(
                (location.latitude, location.longitude), 
                (coords['latitude'], coords['longitude'])
            ).miles
            if dist <= radius:
                within_radius.append((location,round(dist,1)))
                
        within_radius.sort(key=lambda tup: tup[1]) #sorts the location/distance tuples by dist
        

    context = {
        'within_radius': within_radius,
        'radius':radius,
        'location': searched_location,
        'resource': resource,
        'search_from': coords,
        'type': type_
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

def provider_partial(request, provider_id):
	provider = get_object_or_404(Provider, id=provider_id)

	return render(request, 'provider/provider_profile.html', {
													'provider': provider, 
													})

def location_partial(request, location_id):
	location = get_object_or_404(Location, id=location_id)

	return render(request, 'location/profile.html', {
													'current_location': location, 
													})
@login_required
def delete_location(request, location_id):
	location = get_object_or_404(Location, id=location_id)
	provider = location.provider
	admin_user = provider.admin
	if request.user == admin_user: # only the provider's registered user
		location.delete()
		data = {'success': True}
		# currently it's deleting but not returning good data
		return HttpResponse(simplejson.dumps(data), content_type='application/json')
	else:
		return HttpResponseRedirect(reverse('provider_detail', kwargs={'provider_id': provider.id}))

@login_required
def new_location(request, provider_id):
	provider = get_object_or_404(Provider, id=provider_id)
	admin_user = provider.admin
	if request.user == admin_user: # only the provider's registered user
		if request.method == "POST":
			location_form = LocationForm(request.POST)
			if location_form.is_valid():
				location = location_form.save(commit=False)
				location.provider = provider
				location.save()
				data = {
					'location_id': location.id,
				}
				return HttpResponse(simplejson.dumps(data), content_type="application/json")
			else:
				errors_dict = {}
				if location_form.errors:
					for error in location_form.errors:
						e = location_form.errors[error]
						errors_dict[error] = unicode(e)

				return HttpResponseBadRequest(simplejson.dumps(errors_dict))

		else:
			template = 'location/new.html'
			data = {
				'location_form': LocationForm(),
				'provider_id': provider.id,

			}
			return render(request, template, data)
	else:
		return HttpResponseRedirect(reverse('provider_detail', kwargs={'provider_id': provider.id}))


@login_required
def edit_location(request, location_id):
	location = get_object_or_404(Location, id=location_id)
	provider = location.provider
	admin_user = provider.admin
	if request.user == admin_user: # only the provider's registered user
		if request.method == "POST":
			location_form = LocationForm(request.POST,instance=location)
			if location_form.is_valid():
				location = location_form.save()
				template = 'location/profile.html'
				return HttpResponse('OK')
			else:
				errors_dict = {}
				if location_form.errors:
					for error in location_form.errors:
						e = location_form.errors[error]
						errors_dict[error] = unicode(e)

				return HttpResponseBadRequest(simplejson.dumps(errors_dict))
		else:
			template = 'location/edit.html'
			data = {
						'location_form': LocationForm(instance=location),
						'location_id': location.id,
					}
			return render(request, template, data)
	else:
		return HttpResponseRedirect(reverse('provider_detail', kwargs={'provider_id': provider.id}))

@login_required
def edit_provider(request, provider_id):

	provider = get_object_or_404(Provider, id=provider_id)
	admin_user = provider.admin

	if request.user and request.user == admin_user: # only the provider's registered user can edit page

		if request.is_ajax():
			if request.method == 'POST': #and request.is_ajax():
				provider_form = ProviderForm(request.POST,instance=provider)
				if provider_form.is_valid():
					provider = provider_form.save()
					template = 'provider/provider_profile.html'
					data = {
						'provider_id': provider.id,
					}
					return HttpResponse(simplejson.dumps(data), content_type="application/json")
				else:
					errors_dict = {}
					if provider_form.errors:
						for error in provider_form.errors:
							e = provider_form.errors[error]
							errors_dict[error] = unicode(e)

					return HttpResponseBadRequest(simplejson.dumps(errors_dict))
			else:
					template = 'provider/provider_edit.html'
					data = {
						'provider_form': ProviderForm(instance=provider),
						'provider_id': provider.id,
					}
			return render(request, template, data)

		else:
			if request.method == 'POST':
				provider_form = ProviderForm(request.POST,instance=provider)
				password_change_form = PasswordChangeForm(request.POST)
				location_formset = LocationForm(request.POST,request.FILES)

				if password_change_form.is_valid() and provider_form.is_valid() and location_form.is_valid():
					password_change_form.save()
					provider = provider_form.save(commit=False)
					provider.admin = admin_user
					provider.save()
					for location_form in location_formset:
						location = location_form.save(commit=False)
						location.provider = provider
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
													'password_change_form': password_change_form,
													 })

	else:
		return HttpResponseRedirect(reverse('provider_detail', kwargs={'provider_id': provider.id}))

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
			profile_form = UserForm(request.POST)
			if profile_form.is_valid():
				user = Volunteer()
				user.first_name = profile_form.cleaned_data.get("first_name")
				user.last_name = profile_form.cleaned_data.get("last_name")
				user.email = profile_form.cleaned_data.get("email")
				user.phone = profile_form.cleaned_data.get("phone")
				user.address = profile_form.cleaned_data.get("address")
				user.save()
				# Still need to check for saving of skills they have here
				return HttpResponseRedirect(reverse('resources'))
		else:
			profile_form = UserForm()
		return render(request, "volunteer/new.html", { 'profile_form': profile_form})

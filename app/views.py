# -*- coding: utf-8 -*-
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
from django.core.mail import send_mass_mail
from email_texts import admin_email_address
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


RADIUS_DISTANCE = 35 # miles


def index(request):
    return render(request, "index.html")

def about(request):
    return render(request, "about.html")

def privacy(request):
    return render(request, "privacy.html")

def FAQ(request):
    return render(request, "FAQ.html")
    
def find_search_coordinates(searched_location):
    #helper function, not meant to be connected in urls.py
    #putting the geocoding of search addresses into a separate method to stay DRY
    #takes the address searched for, returns coordinates
    
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

    return coords

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

    if not searched_location and not resource: # neither
        return render(request, 'resources.html', { 'type': type_ })
    elif searched_location and resource: # both
        # Save the search
        search = Search(**{
                'location': searched_location,
                'resource': resource
            })
        search.save()

        coords = find_search_coordinates(searched_location)
    elif not searched_location:
        coords = False

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
            
        preferred_orgs = False
        within_radius = []
        for location in locations:
            dist = vincenty(
                (location.latitude, location.longitude), 
                (coords['latitude'], coords['longitude'])
            ).miles
            if dist <= radius:
                within_radius.append((location,round(dist,1)))
                if location.provider.preferred:
                    preferred_orgs = True

        within_radius.sort(key=lambda tup: (not(tup[0].provider.preferred), tup[1]))
        #sorts the location/distance tuples by dist with preferred ones first
        
        
        #passing a sorted list of tuples with (orgname, distance)
        

    context = {
        'within_radius': within_radius,
        'radius':radius,
        'preferred_orgs':preferred_orgs,
        'location': searched_location,
        'resource': resource,
        'search_from': coords,
        'type': type_
    }

    return render(request, 'resources.html', dictionary=context)

@login_required
def profile(request):
#    provider = get_object_or_404(City, pk=provider_id)
    return render(request, "profile.html")
#    return render(request, "profile.html", {'provider': provider })

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
        return HttpResponseRedirect(reverse('index'))

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
    # Users should only be able to make one provider, so send the user back to the home page if they try to add a new provider.
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('index'))
    # If no user is logged in, let them register a new provider.
    else:
        # Load the fields for a location from the model - except the provider field, since the organization and its office are automatically linked when the form is submitted
        LocationFormset = modelformset_factory(Location, exclude=('provider',))
        # When submit is clicked, post the data that's been entered into each field so it can be checked
        if request.method == "POST":
            admin_form = UserCreationForm(request.POST)
            provider_form = ProviderForm(request.POST)
            location_formset = LocationFormset(request.POST)
            # Check to make sure all of the form data is entered and valid
            if admin_form.is_valid() and provider_form.is_valid() and location_formset.is_valid():
                u_name = admin_form.cleaned_data.get('username')
                u_pass = admin_form.cleaned_data.get('password2')
                admin = admin_form.save()
                # At this point we've committed a user, but the line below is going to have us save a provider object so we can use it to save a location, but not yet take the time to make a database commit
                provider = provider_form.save(commit=False)
                provider.admin = admin
                provider.save()
                resources_needed = []
                resources_available = []
                
                
                # Grab email set dependent on language value
                if request.LANGUAGE_CODE == 'es':
                    from email_texts import spanish_version_emails as emails
                else:
                    from email_texts import english_version_emails as emails
                    
                    
                # At this point we've saved a user and a provider, and have blank lists of resources ready to accept info about the location
                for location_form in location_formset: # The formset may have more than one form in it - more get added on the template via javascript. So we have to loop through and save data from each one here.
                    location = location_form.save(commit=False) # The commit=false here lets us create a provider and a location, then connect them, THEN save everthing in the database. Saves time making database commits.
                    location.provider = provider
                    location.save()
                    location_form.save_m2m() # We have to use the .save many-to-many function because we used commit=False earlier
                    
                    # If there are resources needed or available at any location, grab them from each location and combine them in a list that gets associated with the provider
                    #needed so we can send them in the email
                    #note that this messy loop is to prevent repeats AND to deal with translation
                    #and is all around generally a pretty terrible hack

                    for r in location.resources_needed.all():
                        if r.name.lower() in emails['resource_translation']:
                            translated_name = emails['resource_translation'][r.name.lower()]
                            if translated_name not in resources_needed:
                                resources_needed.append(translated_name)

                    for r in location.resources_available.all():
                        if r.name.lower() in emails['resource_translation']:
                            translated_name = emails['resource_translation'][r.name.lower()]
                            if translated_name not in resources_needed:
                                resources_available.append(translated_name)
                        
                location_formset.save() # Now that we've added up resources, save the whole formset.

        
                

                    
                # Transform resources lists into strings (or 'None' if none) for e-mail sending
                if len(resources_needed) > 0:
                    resources_needed = ', '.join(resources_needed)
                else:
                    resources_needed = 'None'
        
                if len(resources_available) > 0:
                    resources_available = ', '.join(resources_available)
                else:
                    resources_available = 'None'
        
                # Grab admin email list (if not already grabbed or stored somewhere else)
                admin_email_list = [admin_email_address]
        
                # Build confirmation email
                email = emails['provider_signup']['confirmation']
                email['body'] = email['body'].format(provider_name = provider.name,
                    org_username=provider.admin.username,
                    resources_needed=resources_needed,
                    resources_available=resources_available)
                confirmation_email = (email['subject'], email['body'], email['from'], [provider.admin.username])

                # Build admin notification email
                email = emails['provider_signup']['admin']
                email['body'] = email['body'].format(org_username=provider.admin.username)
                admin_email = (email['subject'], email['body'], email['from'], admin_email_list)
        
                # Send Them
                try:
                    send_mass_mail((admin_email, confirmation_email), fail_silently=False)
                except:
                    pass
                

                # Authenticate and log in the user
                user = authenticate(username=u_name,
                                    password=u_pass)
                login(request, user)
                return HttpResponseRedirect(reverse('provider_detail', kwargs={'provider_id': provider.id}))
        
        # If we've just arrived on the page, load the blank form(s)
        else:
            admin_form = UserCreationForm() # The piece of the new provider form that takes info on its primary staff person
            provider_form = ProviderForm()  # The piece of the new provider form that takes info about the organization
            location_formset = LocationFormset(queryset=Location.objects.none()) # The piece of the new provider form that takes info about the organization's first office location, and assumes you have no locations loaded yet

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
        return HttpResponseRedirect(reverse('index'))

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
                
                user_resources = profile_form.cleaned_data.get("has_resources")
                
                user_resource_objects = [Resource.objects.filter(name=r).first() for r in user_resources]

                for r in user_resource_objects:
                    user.has_resources.add(r)
                
                user.save()
                
                    

        
                # Grab email set dependent on language value (may need to change values)
                if request.LANGUAGE_CODE == 'es':
                    from email_texts import spanish_version_emails as emails
                else:
                    from email_texts import english_version_emails as emails
                    
                # Find some nearby locations that need the things the volunteer has
                coords = find_search_coordinates(user.address)
                
                within_radius = []
                
                if len(user_resource_objects) == 0:
                    #do not include anything about local orgs if the user specified no resources
                    pass
                elif not coords:
                    #do not include local orgs if the coordinates weren't found
                    pass
                elif len(user_resource_objects) == 1 and user_resource_objects[0].name.lower() == "other":
                    #do not include local orgs if the only resource is "other"
                    pass
                else:
                    locations = Location.objects.select_related('provider').exclude(provider__approved=False)
                    locations = locations.filter(resources_needed__in=user_resource_objects)
                    locations = set(locations)
                    
                    for location in locations:
                        dist = vincenty(
                            (location.latitude, location.longitude), 
                            (coords['latitude'], coords['longitude'])
                            ).miles
                    
                        if dist <= RADIUS_DISTANCE:
                            within_radius.append((location,round(dist,1)))
                        
                    
                    within_radius.sort(key=lambda tup: tup[1])
                    
                    within_radius = within_radius[0:3] #only display the 3 nearest locations in email
                
                vol_conf_texts = emails['volunteer_signup']['confirmation']
                if len(within_radius) > 0:
                    getting_started = vol_conf_texts["here_are_some_orgs"].decode('utf-8')
                    for location_tuple in within_radius:
                        location = location_tuple[0]
                        dist = location_tuple[1]
                        
                        location_resources = []
                        for r in location.resources_needed.all():
                            if r.name in emails['resource_translation']:
                                location_resources.append(emails['resource_translation'][r.name])

                        location_info = [location.provider.name.decode('utf-8'),
                                        location.address,location.phone.decode('utf-8'),
                                        location.provider.URL.decode('utf-8'),
                                        "{0} {1}".format(dist,vol_conf_texts["miles_from_you"].decode('utf-8')),
                                        "{0} {1}".format(vol_conf_texts["resources_needed"].decode('utf-8'),', '.join(location_resources)),
                                        '\n\n']
                        getting_started = getting_started.decode('utf-8')
                        getting_started += '\n'.join(location_info)
                    getting_started += vol_conf_texts["find_some_more_orgs"].decode('utf-8')
                else:
                    getting_started = vol_conf_texts["find_some_orgs"].decode('utf-8')
                    
                getting_started += " http://www.buscandomaryland.com/resources/volunteer"
                    
                # Grab admin email list (if not already grabbed or stored somewhere else)
                admin_email_list = [admin_email_address]
                
                vol_resources = []
                for r in user_resources:
                    if r in emails['resource_translation']:
                        vol_resources.append(emails['resource_translation'][r.lower()])
                
                if len(vol_resources) > 0:
                    vol_resources = ','.join(vol_resources)
                else:
                    vol_resources = "None"
        
                # Build confirmation email
                email = emails['volunteer_signup']['confirmation']
                volunteer_email_body = email['body'].format(firstname=user.first_name,
                    vol_username=user.email,
                    vol_location=user.address,
                    resources_available=vol_resources,
                    getting_started = getting_started)
                confirmation_email = (email['subject'], volunteer_email_body, email['from'], [user.email])
        
                # Build admin notification email
                email = emails['volunteer_signup']['admin']
                admin_email_body = email['body'].format(vol_username=user.email)
                admin_email = (email['subject'], admin_email_body, email['from'], admin_email_list)
        
                # Send Them
                try:
                    send_mass_mail((admin_email, confirmation_email), fail_silently=False)
                except:
                    pass
                #end of code for confirmation e-mail
                
                
                # Still need to check for saving of skills they have here
                return HttpResponseRedirect(reverse('resources'))
        else:
            profile_form = UserForm()
        return render(request, "volunteer/new.html", { 'profile_form': profile_form})

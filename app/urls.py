from django.conf.urls import patterns, include, url
from app import views


urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^index/$', views.index, name='index'),
    url(r'^about/$', views.about, name='about'),
    url(r'^individual_home/$', views.index, name='individual_home'),
    url(r'^organization_home/$', views.index, name='organization_home'),
    url(r'^organization/register/$', views.organization_register, name='organization_register'),
    url(r'^family_home/$', views.index, name='family_home'),
    url(r'^profile/(?P<organization_id>\d+)/$', views.index, name='index'),
    url(r'^signup/$', views.index, name='signup'),
    url(r'^lookfor/$', views.index, name='lookfor'),
    url(r'^resources/$', views.resources, name='resources'),
    url(r'^provider/new/$', views.add_provider, name='add_provider'),
    url(r'^provider/(?P<provider_id>\d+)/edit/$', views.edit_provider, name='edit_provider'),
    #url(r'^provider/form_upload/$', views.add_provider, name='add_provider'),
    url(r'^provider/(?P<provider_id>\d+)/detail.html$', views.provider_detail, name='provider_detail'),
)
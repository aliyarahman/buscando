from django.conf.urls import patterns, include, url
from app import views
from django.contrib.auth.views import login, logout, password_reset
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm

urlpatterns = patterns('',
    url(r'^login/$', views.login_page, name='login'),
    url(r'^logout/$', views.logout_page, name='logout'),
    url(r'^$', views.index, name='index'),
    url(r'^about/$', views.about, name='about'),
    url(r'^individual_home/$', views.index, name='individual_home'),
    url(r'^organization_home/$', views.organization_home, name='organization_home'),
    url(r'^family_home/$', views.index, name='family_home'),
    url(r'^profile/(?P<organization_id>\d+)/$', views.provider_detail, name='index'), #remove
    url(r'^signup/$', views.index, name='signup'), #remove
    url(r'^lookfor/$', views.index, name='lookfor'),
    url(r'^resources/$', views.resources, name='resources'),
    url(r'^provider/new/$', views.add_provider, name='add_provider'),
    url(r'^organization/register/$', views.organization_register, name='organization_register'), #temporary until integrate bootstrap
    url(r'^provider/(?P<provider_id>\d+)/edit/$', views.edit_provider, name='edit_provider'),
    url(r'^provider/(?P<provider_id>\d+)/$', views.provider_detail, name='provider_detail'),
    url(r'^provider/(?P<provider_id>\d+)/delete/$', views.delete_provider, name='delete_provider'),
)
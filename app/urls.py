from django.conf.urls import patterns, include, url
from app import views


urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^index/$', views.index, name='index'),
    url(r'^individual_home/$', views.index, name='individual_home'),
    url(r'^organization_home/$', views.index, name='organization_home'),
    url(r'^family_home/$', views.index, name='family_home'),
    url(r'^profile/(?P<organization_id>\d+)/$', views.index, name='index'),
    url(r'^signup/$', views.index, name='index'),
    url(r'^lookfor/$', views.index, name='index'),
    url(r'^resources/$', views.index, name='index'),
)

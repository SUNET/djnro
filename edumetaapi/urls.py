from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^location$', views.LocationView.as_view(), name='location'),
    url(r'^location/(?P<id>[0-9]*)$', views.LocationView.as_view(), name='location'),
    url(r'^institution', views.InstitutionView.as_view(), name='institution'),
    url(r'^institution/(?P<id>[0-9]*)$', views.InstitutionView.as_view(), name='institution'),
]

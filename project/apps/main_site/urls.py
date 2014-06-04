from django.conf.urls.defaults import patterns, include, url

from main_site import views

urlpatterns = patterns('',
    url(r'^about$', views.home, name='home'),
    url(r'(?P<url>.*)', views.confirm, name='confirm'),
    # url(r'(.*', views.confirm, name='confirm'),
)

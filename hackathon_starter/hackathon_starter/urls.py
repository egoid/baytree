from django.conf.urls import patterns, include, url
from django.contrib import admin
from hackathon import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^register/$', views.register, name='register'),
    url(r'^submit_order/$', views.submit_order, name='submit_order'),
    url(r'^login/$', views.login, name='login'),
    url(r'^upload/$', views.upload, name='upload'),
    url(r'^admin/', include(admin.site.urls)),
)

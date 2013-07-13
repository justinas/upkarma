from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index),
    url(r'^user/(.+)/$', views.user),
    url(r'^search/$', views.search),
    url(r'^auth/login/$', views.auth.start_login),
    url(r'^auth/callback/$', views.auth.callback),
    url(r'^auth/logout/$', views.auth.logout_view),
)

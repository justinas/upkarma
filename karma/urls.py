from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter

from . import views
from karma.news import views as news_views

api_router = DefaultRouter()
api_router.register(r'users', views.api.UserViewSet)
api_router.register(r'tweets', views.api.TweetViewSet)

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='karma.views.index'),
    url(r'^user/(.+)/$', views.user, name='karma.views.user'),
    url(r'^search/$', views.search, name='karma.views.search'),
    url(r'^stats/$', views.stats, name='karma.views.stats'),
    url(r'^api/', include(api_router.urls)),

    url(r'^auth/login/$', views.auth.start_login),
    url(r'^auth/callback/$', views.auth.callback),
    url(r'^auth/logout/$', views.auth.logout_view),
    url(r'^auth/no-user/$', views.auth.no_user),

    url(r'^news/$', news_views.news_list),
    url(r'^news/(\d+)/$', news_views.news_single),
    url(r'^guide/$', views.guide, name='karma.views.guide'),
)

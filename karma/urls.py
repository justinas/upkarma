from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from . import views
from karma.news import views as news_views

api_router = DefaultRouter()
api_router.register(r'users', views.api.UserViewSet)
api_router.register(r'tweets', views.api.TweetViewSet)

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^user/(.+)/$', views.user, name='user'),
    url(r'^search/$', views.search, name='search'),
    url(r'^stats/$', views.stats, name='stats'),
    url(r'^api/', include(api_router.urls)),

    url(r'^auth/login/$', views.auth.start_login, name='start-login'),
    url(r'^auth/callback/$', views.auth.callback, name='auth-callback'),
    url(r'^auth/logout/$', views.auth.logout_view, name='logout-view'),
    url(r'^auth/no-user/$', views.auth.no_user, name='no-user'),

    url(r'^news/$', news_views.news_list, name='news-list'),
    url(r'^news/(\d+)/$', news_views.news_single, name='news-single'),
    url(r'^guide/$', views.guide, name='guide'),
]

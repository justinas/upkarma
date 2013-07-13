from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from requests_oauthlib import OAuth1Session

from karma.models import User

def get_oauth_session(token=None, token_secret=None, callback_uri=None):
    creds = settings.UPKARMA_SETTINGS['app_credentials']
    sess = OAuth1Session(client_key=creds['consumer_key'],
                         client_secret=creds['consumer_secret'],
                         callback_uri=callback_uri,
                         resource_owner_key=token,
                         resource_owner_secret=token_secret)

    return sess

def start_login(request):
    """
    Starts the login process by
    obtaining the request token
    and redirecting the user
    """

    sess = get_oauth_session(callback_uri=settings.UPKARMA_SETTINGS['callback_uri'])
    tokens = sess.fetch_request_token(
        'https://api.twitter.com/oauth/request_token'
    )

    request.session['request_token'] = tokens['oauth_token']
    request.session['request_token_secret'] = tokens['oauth_token_secret']

    redirect_url = sess.authorization_url('https://api.twitter.com/oauth/authorize')

    return HttpResponseRedirect(redirect_url)


def callback(request):
    """
    Exchanges the request token
    for an access token
    """
    sess = get_oauth_session(token=request.session['request_token'],
                             token_secret=request.session['request_token_secret'])

    uri = request.build_absolute_uri()

    sess.parse_authorization_response(uri)

    tokens = sess.fetch_access_token('https://api.twitter.com/oauth/access_token')
    request.session['oauth_token'] = tokens['oauth_token']
    request.session['oauth_token_secret'] = tokens['oauth_token_secret']

    # log them in
    user = authenticate(twitter_id=tokens['user_id'])
    if user is None:
        raise Exception('TODO: redirect to error page')

    login(request, user)

    return HttpResponseRedirect(reverse('karma.views.index'))

def logout_view(request):
    logout(request)

    return HttpResponseRedirect(reverse('karma.views.index'))

from twitter import Twitter, TwitterStream, OAuth
from django.conf import settings
from datetime import date, timedelta

def get_global_client():
    """
    The global client is used for
    the bot and in other places where
    user-specific permissions aren't required
    """
    t = Twitter(auth=OAuth(**settings.UPKARMA_SETTINGS['global_credentials']))
    return t

def get_stream_client():
    t = TwitterStream(auth=OAuth(**settings.UPKARMA_SETTINGS['global_credentials']))
    return t

def get_week_start(today=None):
    if not today:
        today = date.today()
    # subtract the amount of days
    # that has passed since Monday
    return today - timedelta(days=today.weekday())

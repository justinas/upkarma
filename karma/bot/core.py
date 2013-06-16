from django.conf import settings
from twitter import Twitter, OAuth

def get_bot_client():
    t = Twitter(auth=OAuth(**settings.UPKARMA_SETTINGS['bot_credentials']))
    return t

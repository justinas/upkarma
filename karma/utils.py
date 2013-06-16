from twitter import Twitter, OAuth
from django.conf import settings

def get_global_client():
    """
    The global client is used for
    the bot and in other places where
    user-specific permissions aren't required
    """
    t = Twitter(auth=OAuth(**settings.UPKARMA_SETTINGS['bot_credentials']))
    return t

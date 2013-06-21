from redis import StrictRedis
from twitter import Twitter, OAuth
from datetime import date, timedelta

from django.conf import settings

from .stream import TwitterStream

def flatten_qs(qs):
    """
    Flattens the query string dictionary
    returned by parse_qs
    """
    return dict((i, qs[i][0]) for i in qs)

def get_global_client():
    """
    The global client is used for
    the bot and in other places where
    user-specific permissions aren't required
    """
    t = Twitter(auth=OAuth(**settings.UPKARMA_SETTINGS['global_credentials']))
    return t

def get_stream_client():
    t = TwitterStream(**settings.UPKARMA_SETTINGS['global_credentials'])
    return t

def get_redis_client():
    return StrictRedis(**settings.UPKARMA_SETTINGS['redis'])

def get_week_start(today=None):
    if not today:
        today = date.today()
    # subtract the amount of days
    # that has passed since Monday
    return today - timedelta(days=today.weekday())

def tweetback(message, tweet):
    """
    Replies to the author of tweet
    with a specified message
    """
    client = get_global_client()
    message = u'@{0} {1}'.format(tweet['user']['screen_name'], message)
    try:
        client.statuses.update(status=message,
                            in_reply_to_status_id=tweet['id_str'])
    except TwitterError as e:
        # TODO: log
        pass


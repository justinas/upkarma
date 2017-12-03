from redis import StrictRedis
from twitter import Twitter, OAuth, TwitterError
from datetime import date, datetime, timedelta
from time import mktime
import logging

from django.conf import settings
from django.core.cache import cache

from .stream import TwitterStream

def ym_to_js_timestamp(string):
    y, m = (int(i) for i in string.split('-'))
    dt = datetime(y, m, 1)

    unix = mktime(dt.timetuple())
    # JavaScript counts in milliseconds
    unix *= 1000

    return unix

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

def cached(key, timeout=None):
    """
    A decorator that either returns
    the function result from django cache
    according to the key if it exists there
    or calls the function, stores the result in cache
    and then returns it.

    str.format(*args, **kwargs) is called on the cache key
    with the arguments the function is called with
    """
    def decorator(func):
        def wrap(*args, **kwargs):
            _bypass_cache = kwargs.pop('_bypass_cache', False)
            final_key = key.format(*args, **kwargs)
            result = cache.get(final_key)

            if (not result) or _bypass_cache:
                result = func(*args, **kwargs)
                cache.set(final_key, result, timeout)

            return result
        return wrap

    return decorator

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
    log = logging.getLogger('karma.other')
    client = get_global_client()
    message = '@{0} {1}'.format(tweet['user']['screen_name'], message)
    if settings.DEBUG:
        # Don't tweet
        log.debug('Not tweeted because of DEBUG=True: '+message)
        return
    try:
        client.statuses.update(status=message,
                            in_reply_to_status_id=tweet['id_str'])
        log.debug('Tweeted: `{0}`'.format(message))
    except TwitterError as e:
        log.error('Tweet `{0}` failed with an exception:\n{1}'.format(message,e))
        pass


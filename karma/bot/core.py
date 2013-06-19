# -*- encoding: utf-8 -*-
import re
from twitter import Twitter, OAuth

try:
    from urlparse import parse_qs
except ImportError:
    from urllib.parse import parse_qs

from django.conf import settings
from django.core.exceptions import ValidationError

from ..exceptions import BadFormat, SenderBanned, ReceiverBanned
from ..models import User, Tweet
from ..utils import tweetback

DATE_FORMAT = '%a %b %d %H:%M:%S +0000 %Y'

def parse_date(str)
    return datetime.strptime(str, DATE_FORMAT)


def process_tweet(tweet):
    """
    Processes a single tweet object,
    as specified at https://dev.twitter.com/docs/platform-objects/tweets,
    but decoded already decoded from JSON
    """
    mentions = tweet['entities']['user_mentions']
    if not mentions:
        raise BadFormat(u'Nenurodėte, kokiam vartotojui duoti karmos')
    if len(mentions) > 1:
        raise BadFormat(u'Žinutėje daugiau negu vienas vartotojas '
                        u'– karmos nebus duota')

    receiver_data = mentions[0]

    sender_data = tweet['user']
    text = tweet['text']

    # this cleans out the username from the text
    inds = receiver_data['indices']
    clean_text = tweet['text'][:inds[0]] + tweet['text'][inds[1]:]

    # extract the amount from text
    try:
        amount = int(
            re.findall(settings.UPKARMA_SETTINGS['re_amount'], clean_text)[0]
        )
    except IndexError:
        raise BadFormat(u'Nenurodyta, kiek karmos taškų skirti')

    # finding the sender
    try:
        sender = User.objects.get(twitter_id=sender_data['id_str'])
    except User.DoesNotExist:
        # This shall be treated as the **sender** not existing
        # (as non-existant receivers are created)
        # and left to be handled by the caller
        raise

    # finding the receiver
    try:
        receiver = User.objects.get(twitter_id=receiver_data['id_str'])
    except User.DoesNotExist:
        receiver = User.from_twitter_id(receiver_data['id_str'])

    try:
        t = Tweet(receiver=receiver, sender=sender, amount=amount,
                  text=text, twitter_id=tweet['id_str'],
                  date=parse_date(tweet['created_at'])
        t.save()
    except ValidationError:
        # let the caller handle it
        raise

def process_or_tweetback(tweet):
    """
    Processes the tweet
    and, in case of an error,
    tweetsback at the user
    with the error message
    """
    try:
        process_tweet(tweet)
        # no error, nothing to do here
        return
    except BadFormat as e:
        msg = e.args[0]
    except User.DoesNotExist:
        msg = u'Jūs dar nedalyvaujate žaidime. ' \
            u'Paprašykite žaidėjų vieno karmos taško.'
    except ValidationError as e:
        msg = e.messages[0]

    tweetback(msg, tweet)

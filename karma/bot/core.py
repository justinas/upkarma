# -*- encoding: utf-8 -*-
import re
from twitter import Twitter, OAuth

from django.conf import settings

from ..exceptions import BadFormat, SenderBanned, ReceiverBanned
from ..models import User

def process_tweet(tweet):
    """
    Processes a single tweet object,
    as specified at https://dev.twitter.com/docs/platform-objects/tweets,
    but decoded already decoded from JSON
    """
    mentions = tweet['entities']['user_mentions']
    if not mentions:
        raise BadFormat('Nenurodėte, kokiam vartotojui duoti karmos')
    if len(mentions) > 1:
        raise BadFormat('Žinutėje daugiau negu vienas vartotojas '
                        '– karmos nebus duota')

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
        raise BadFormat('Nenurodyta, kiek karmos taškų skirti')

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

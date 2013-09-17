# -*- encoding: utf-8 -*-
import re
from datetime import datetime
import logging

try:
    from urlparse import parse_qs
except ImportError:
    from urllib.parse import parse_qs

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.timezone import utc

from ..exceptions import BadFormat
from ..models import User, Tweet
from ..utils import (tweetback, get_redis_client, get_global_client,
                     get_stream_client, flatten_qs)

DATE_FORMAT = '%a %b %d %H:%M:%S +0000 %Y'

def parse_date(str):
    d = datetime.strptime(str, DATE_FORMAT)
    d = d.replace(tzinfo=utc)
    return d

class Bot(object):
    def __init__(self):
        self.red = get_redis_client()
        self.log = logging.getLogger('karma.bot')

    def catchup(self, max_id):
        try:
            tweets = self.catchup_tweets(max_id)
            self.log.debug(u'Tweets to catch up with: {0}'.format(
                [t['id_str'] for t in tweets]))
            for t in tweets:
                # skip processed tweets
                if self.red.sismember('processed_ids', t['id_str']):
                    continue
                self.process_or_tweetback(t)
                self.record_processed_id(t['id_str'])
                self.record_max_id(t['id_str'])
        except:
            raise

    def run(self, max_id):
        """
        Supposed to be used by a management command
        Catches up with the tweets,
        then processes the tweet stream infinitely
        """
        self.log.debug(u'Catching up with tweets since {0}'.format(max_id))
        self.catchup(max_id)

        self.log.debug(u'Done catching up')

        client = get_stream_client()

        self.log.debug(u'Starting the stream')
        try:
            stream = client.statuses_filter(
                track=settings.UPKARMA_SETTINGS['hashtag']
            )
            for t in stream:
                self.log.debug(u'A new tweet on stream: {0}'.format(t['id']))
                # skip processed tweets
                if self.red.sismember('processed_ids', t['id_str']):
                    continue
                self.process_or_tweetback(t)
                self.record_processed_id(t['id_str'])
                self.record_max_id(t['id_str'])
        except:
            raise

    def record_processed_id(self, id):
        self.log.debug('Added to processed_ids: {0}'.format(id))
        self.red.sadd('processed_ids', id)

    def record_max_id(self, id):
        self.log.error('New max_id: {0}'.format(id))
        self.red.set('max_id', id)

    def catchup_tweets(self, since_id):
        """
        Returns a list of tweets
        that happened since `since_id` until present
        """
        tw = get_global_client()
        tweets = []
        args = dict(q=settings.UPKARMA_SETTINGS['hashtag'], count=100,
                    result_type='recent', include_entities=1,
                    since_id=since_id)

        # fetch the tweets into a list
        while True:
            results = tw.search.tweets(**args)
            tweets.extend(results['statuses'])
            next_results = results['search_metadata'].get('next_results', None)
            if next_results:
                # remove the ? at the beginning
                args = flatten_qs(parse_qs(next_results[1:]))
            else:
                break

        # so we process the oldest ones first
        tweets.reverse()

        return tweets

    def process_or_tweetback(self, tweet):
        """
        Processes the tweet
        and, in case of an error,
        tweetsback at the user
        with the error message
        """
        self.log.debug(u'process_or_tweetback() id {0}'.format(tweet['id_str']))
        try:
            self.process_tweet(tweet)
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


    def process_tweet(self, tweet):
        """
        Processes a single tweet object,
        as specified at https://dev.twitter.com/docs/platform-objects/tweets,
        but already decoded from JSON
        """
        retweeted = tweet.get('retweeted_status', None)

        if retweeted:
            self.log.debug("Tweet id {0} was a retweet, so it was skipped.".format(tweet['id_str']))
            return

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
            try:
                receiver = User.from_twitter_id(receiver_data['id_str'])
            except TwitterHTTPError as e:
                if e.e.getcode() == 404:
                    # well, user has been deleted
                    raise BadFormat(u'Vartotojas nerastas.')

        try:
            t = Tweet(receiver=receiver, sender=sender, amount=amount,
                    text=text, twitter_id=tweet['id_str'],
                    date=parse_date(tweet['created_at']))
            t.save()
        except ValidationError:
            # let the caller handle it
            raise



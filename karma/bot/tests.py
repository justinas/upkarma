#encoding=utf-8
import json
import sys
from mock import Mock, patch, MagicMock
import httpretty

from django.conf import settings
from django.test import TestCase
from django.core.exceptions import ValidationError

from .core import Bot
from ..stream import TwitterStream
from ..models import User, Tweet
from ..exceptions import BadFormat
from ..tests import get_req_arg, get_base_tweet, ht
from ..utils import flatten_qs, get_redis_client


USER_INFO_BLOB = """
{
  "profile_image_url": "http://a0.twimg.com/profile_images/1777569006/image1327396628_normal.png",
  "id_str": "3",
  "profile_image_url_https": "https://si0.twimg.com/profile_images/1777569006/image1327396628_normal.png",
  "id": 3,
  "screen_name": "guy3"
}
"""

SEARCH_BLOBS = [
    """
    {
    "search_metadata": {
        "max_id": 4,
        "since_id": 2,
        "next_results": "?max_id=2&q=%23upkarma&count=2&include_entities=1&result_type=recent",
        "since_id_str": "2",
        "max_id_str": "4"
    },
    "statuses" : [{}, {}]
    }
    """,
    """
    {
    "search_metadata": {
        "max_id": 6,
        "since_id": 4,
        "since_id_str": "4",
        "max_id_str": "6"
    },
    "statuses" : [{}, {}]
    }
    """,
]


class BotFormatHandlingTest(TestCase):
    def setUp(self):
        self.bot = Bot()
    def test_bot_fails_on_missing_amount(self):
        t = get_base_tweet()
        t['text'] = ht('  @guy2')
        self.assertRaises(BadFormat, self.bot.process_tweet, t)

    def test_bot_fails_on_no_mentions(self):
        t = get_base_tweet()
        t['text'] = ht('  1')
        t['entities']['user_mentions'] = []
        self.assertRaises(BadFormat, self.bot.process_tweet, t)

    def test_bot_fails_on_too_many_mentions(self):
        t = get_base_tweet()
        t['text'] = ht('  1 @abc @def #ghi')
        mention = {"name":"Twitter API", "indices":[4,15],
                   "screen_name":"twitterapi", "id":6253282,
                   "id_str":"6253282"}

        t['entities']['user_mentions'].append(mention)
        t['entities']['user_mentions'].append(mention)
        t['entities']['user_mentions'].append(mention)

        self.assertRaises(BadFormat, self.bot.process_tweet, t)

    def test_bot_extracts_amount_correctly(self):
        t = get_base_tweet()
        t['text'] = ht('  3 @guy1')

class BotUserFindingTest(TestCase):
    def setUp(self):
        self.bot = Bot()

        self.guy1 = User.objects.create(screen_name='guy1', twitter_id='1')
        self.guy2 = User.objects.create(screen_name='guy2', twitter_id='2')

        self.fti_mock = Mock(wraps=User.from_twitter_id)
        self.fti_patch = patch('karma.models.User.from_twitter_id',
                           new=self.fti_mock)
        self.fti_patch.start()

        httpretty.enable()
        httpretty.register_uri(httpretty.GET,
                               "https://api.twitter.com/1.1/users/show.json",
                               body=USER_INFO_BLOB)

    def tearDown(self):
        User.objects.all().delete()
        Tweet.objects.all().delete()

        self.fti_patch.stop()
        httpretty.disable()

    def test_non_existant_sender(self):
        t = get_base_tweet()
        t['user']['id_str'] = '42'
        self.assertRaises(User.DoesNotExist, self.bot.process_tweet, t)

    def test_non_existant_receiver(self):
        """
        from_twitter_id should be called when a receiver doesn't exist
        """

        t = get_base_tweet()
        t['entities']['user_mentions'][0]['screen_name'] = 'guy3'
        t['entities']['user_mentions'][0]['id_str'] = '3'
        t['entities']['user_mentions'][0]['id'] = 3

        self.bot.process_tweet(t)
        self.assertTrue(self.fti_mock.called)
        self.assertEquals(User.objects.count(), 3)
        self.assertEquals(Tweet.objects.count(), 1)

    def test_sender_banned(self):
        """
        Even though we test for those in karma.tests,
        we test ban checking here too to
        ensure that it reraises
        ValidationErrors from Tweet.save()
        """

        self.guy1.banned = True
        self.guy1.save()
        self.assertRaises(ValidationError, self.bot.process_tweet, get_base_tweet())

    def test_receiver_banned(self):
        self.guy2.banned = True
        self.guy2.save()
        self.assertRaises(ValidationError, self.bot.process_tweet, get_base_tweet())

class ProcessOrTweetbackTest(TestCase):
    def setUp(self):
        self.bot = Bot()

        self.guy1 = User.objects.create(screen_name='guy1', twitter_id='1')
        self.guy2 = User.objects.create(screen_name='guy2', twitter_id='2')

    def tearDown(self):
        User.objects.all().delete()
        Tweet.objects.all().delete()

    def test_doesnt_tweetback_on_sucess(self):
        twb = Mock('karma.utils.tweetback')
        self.bot.process_or_tweetback(get_base_tweet())
        self.assertFalse(twb.called)

    @httpretty.activate
    def test_tweets_back_errors_correctly(self):
        httpretty.register_uri(httpretty.POST,
                               'https://api.twitter.com/1.1/statuses/update.json',
                               body=json.dumps('{}'))
        # BadFormat
        t = get_base_tweet()
        t['text'] = ht(' ')

        self.bot.process_or_tweetback(t)
        self.assertTrue(get_req_arg('status').startswith(u'@guy1 Nenurodyta'))

        # User.DoesNotExist
        t = get_base_tweet()
        t['user']['id_str'] = '12435'
        self.bot.process_or_tweetback(t)
        self.assertTrue(get_req_arg('status').startswith(u'@guy1 Jūs dar'))

        # ValidationError
        self.guy1.banned = True
        self.guy1.save()
        t = get_base_tweet()
        self.bot.process_or_tweetback(t)
        self.assertTrue(get_req_arg('status').startswith(u'@guy1 Jūs buvote'))

class CatchupTest(TestCase):
    def setUp(self):
        self.bot = Bot()
        self.bot.red = MagicMock()

    @httpretty.activate
    def test_finds_all_tweets(self):
        httpretty.register_uri(httpretty.GET,
                'https://api.twitter.com/1.1/search/tweets.json',
                responses=[
                    httpretty.Response(body=SEARCH_BLOBS[0], status=200),
                    httpretty.Response(body=SEARCH_BLOBS[1], status=200)
                ])

        tweets = self.bot.catchup_tweets(0)
        self.assertEquals(len(tweets), 4)

        requests = httpretty.HTTPretty.latest_requests
        self.assertEquals(len(requests), 2)

        self.assertEquals(flatten_qs(requests[1].querystring)['max_id'], '2')
"""
        tweet = get_base_tweet()
        tweet['id'] = 1000
        tweet['id_str'] = '1000'


        tweet2 = get_base_tweet()
        tweet2['id'] = 1500
        tweet2['id_str'] = '1500'

        httpretty.register_uri(httpretty.POST, TwitterStream.URL,
                               streaming=True,
                               body=[json.dumps(tweet), '\r\n',
                                     json.dumps(tweet2), '\r\n'])
        # catchup
        httpretty.register_uri(httpretty.GET,
                'https://api.twitter.com/1.1/search/tweets.json',
                responses=[
                    httpretty.Response(body=SEARCH_BLOBS[0], status=200),
                    httpretty.Response(body=SEARCH_BLOBS[1], status=200)
                ])
"""

class BotRedisTest(TestCase):
    def setUp(self):
        self.bot = Bot()
        self.bot.catchup_tweets = Mock(return_value=[{'id_str' : '2'},
                                                     {'id_str' : '4'}])
        self.bot.process_or_tweetback = MagicMock()
        self.bot.red = self.redis = MagicMock()

        # so bot never skips tweets as already processed
        self.redis.sismember.return_value = False

        ### httpretty

        tweet = get_base_tweet()
        tweet['id_str'] = '1234'
        tweet_body = json.dumps(tweet)

        httpretty.register_uri(httpretty.POST, TwitterStream.URL,
                               streaming=True,
                               body=[tweet_body, '\r\n'])
        httpretty.enable()

    def tearDown(self):
        httpretty.disable()

    def test_records_on_catchup(self):
        self.bot.catchup(0)
        sadd = self.redis.sadd
        _set = self.redis.set

        sadd.assert_any_call('processed_ids', '2')
        sadd.assert_any_call('processed_ids', '4')

        _set.assert_any_call('max_id', '2')
        _set.assert_any_call('max_id', '4')

    def test_records_on_run(self):
        self.bot.run(0)

        sadd = self.redis.sadd
        _set = self.redis.set

        sadd.assert_any_call('processed_ids', '1234')
        _set.assert_any_call('max_id', '1234')

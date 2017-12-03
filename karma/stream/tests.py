from django.test import TestCase
import httpretty
import json
from twitter import TwitterError

from ..tests import get_base_tweet
from ..utils import flatten_qs

from .core import TwitterStream

class StreamTestCase(TestCase):
    def setUp(self):
        httpretty.enable()

        self.base_tweet = get_base_tweet()
        self.tweet_body = tweet_body = json.dumps(get_base_tweet())
        httpretty.register_uri(httpretty.POST, TwitterStream.URL,
                               streaming=True,
                               body=[tweet_body, '\r\n', '\r\n',
                                     tweet_body, '\r\n'])

    def tearDown(self):
        httpretty.disable()

    def test_yields_tweets_correctly(self):
        tweet = json.loads(self.tweet_body)
        stream = TwitterStream('dummy', 'dummy', 'dummy', 'dummy')
        tweets = [t for t in stream.statuses_filter()]
        self.assertEqual(len(tweets), 2)
        self.assertEqual(tweet['id'], tweets[0]['id'])

    def test_passes_args_correctyle(self):
        args = {'track' : 'trains', 'oh' : 'hai'}
        stream = TwitterStream('dummy', 'dummy', 'dummy', 'dummy')

        for t in stream.statuses_filter(**args):
            pass

        req = httpretty.HTTPretty.last_request

        qs = flatten_qs(req.querystring)

        self.assertEqual(qs['track'], args['track'])
        self.assertEqual(qs['oh'], args['oh'])

    def test_raises_on_unknown_message(self):
        httpretty.register_uri(httpretty.POST, TwitterStream.URL,
                               streaming=True,
                               body=[self.tweet_body, '\r\n', '\r\n',
                                    '{"wtf" : "unknown"}'])

        stream = TwitterStream('dummy', 'dummy', 'dummy', 'dummy')
        it = stream.statuses_filter()
        # a tweet
        tw = next(it)
        # the unknown error
        self.assertRaises(TwitterError, next, it)

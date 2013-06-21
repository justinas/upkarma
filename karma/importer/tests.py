from datetime import datetime

from django.conf import settings
from django.test import TestCase
from django.db.models import Sum

from .core import import_from_dump
from ..models import Tweet, User
from ..tests import ht

HASHTAG = settings.UPKARMA_SETTINGS['hashtag']

class ImporterTestCase(TestCase):
    USER_BLOB = """
    [{
    "fields": {
        "avatar": "http://nice.url",
        "banned": false,
        "full_name": null,
        "points": 2304,
        "twitter_id": "42",
        "username": "cool_guy"
    },
    "model": "karma.user",
    "pk": 1
    },
    {
    "fields": {
        "avatar": "http://not_nice.url",
        "banned": false,
        "full_name": null,
        "points": 127,
        "twitter_id": "43",
        "username": "uncool_guy"
    },
    "model": "karma.user",
    "pk": 2
    }
    ]"""

    TWEET_BLOB = """
    [{
    "fields": {
        "amount": 5,
        "date": "2011-11-26T14:17:18",
        "receiver": 1,
        "sender": 2,
        "text": "%s 5 @cool_guy",
        "twitter_id": "5678"
    },
    "model": "karma.tweet",
    "pk": 1
    },

    {
    "fields": {
        "amount": 1,
        "date": "2011-11-26T14:18:41",
        "receiver": 2,
        "sender": 1,
        "text": "%s 1 ta\u0161kas @Apsega",
        "twitter_id": "140434086970929153"
        },
    "model": "karma.tweet",
    "pk": 2
    }]""" % (HASHTAG, HASHTAG)

    RT_BLOB = """
    [{
    "fields":
        {
        "amount": 5,
        "date": "2011-11-26T14:17:18",
        "receiver": 1,
        "sender": 2,
        "text": "RT @cool_guy: %s 5 @lulz",
        "twitter_id": "5678"
        },
    "model": "karma.tweet",
    "pk": 3
    }]
    """ % HASHTAG

    def setUp(self):
        import_from_dump(self.USER_BLOB)

    def tearDown(self):
        Tweet.objects.all().delete()
        User.objects.all().delete()

    def test_creates_a_user(self):
        self.assertEquals(User.objects.count(), 2)
        u = User.objects.get(pk=1)

        # username is now screen_name
        self.assertEquals(u.screen_name, "cool_guy")
        self.assertEquals(u.twitter_id, "42")

    def test_creates_tweets(self):
        import_from_dump(self.TWEET_BLOB)

        self.assertEquals(Tweet.objects.count(), 2)

        t1 = Tweet.objects.get(pk=1)
        t2 = Tweet.objects.get(pk=2)

        self.assertEquals(t1.amount, 5)
        self.assertEquals(t2.amount, 1)

        self.assertEquals(t1.date, datetime(2011, 11, 26, 14, 17, 18))
        self.assertEquals(t1.text, ht(" 5 @cool_guy"))

        cnt1 = User.objects.filter(pk=1).aggregate(
            s=Sum('karma_receives__amount'))['s']
        cnt2 = User.objects.filter(pk=2).aggregate(
            s=Sum('karma_receives__amount'))['s']

        self.assertEquals(cnt1, 5)
        self.assertEquals(cnt2, 1)

    def test_skips_a_retweet(self):
        import_from_dump(self.RT_BLOB)
        self.assertEquals(Tweet.objects.count(), 0)

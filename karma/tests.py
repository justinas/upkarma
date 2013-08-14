import httpretty
import json
from datetime import datetime

from django.conf import settings
from django.test import TestCase
from django.core.exceptions import ValidationError
from mock import MagicMock, patch

try:
    from urlparse import parse_qs
except ImportError:
    from urllib.parse import parse_qs

from .models import Tweet, User
from .utils import tweetback, cached

HASHTAG = settings.UPKARMA_SETTINGS['hashtag']

def ht(string):
    """
    Prepends the current hashtag to a string
    """
    return HASHTAG+string

def get_req_arg(key):
    """
    Gets an arg from httpretty's last request
    """
    args = parse_qs(httpretty.HTTPretty.last_request.body)
    return args[key][0].decode('utf-8')

def get_base_tweet():
    """
    This function returns a tweet template
    we then build upon in tests.
    The template is a perfectly valid tweet
    for upkarma.
    """
    return json.loads("""
    {
    "created_at": "Mon Sep 24 03:35:21 +0000 2012",
    "id_str": "1",
    "entities": {
        "user_mentions": [
            {"name":"Guy 2",
            "indices":[11,16],
            "screen_name":"guy2",
            "id":2,
            "id_str":"2"}
        ]
    },
    "text": "%s 5 @guy2",
    "in_reply_to_status_id_str": null,
    "id": 1,
    "user": {
        "name": "Guy 1",
        "profile_image_url": "http://a0.twimg.com/profile_images/2284174872/7df3h38zabcvjylnyfe3_normal.png",
        "id_str": "1",
        "profile_image_url_https": "https://si0.twimg.com/profile_images/2284174872/7df3h38zabcvjylnyfe3_normal.png",
        "id": 1,
        "profile_background_image_url": "http://a0.twimg.com/images/themes/theme1/bg.png",
        "screen_name": "guy1"
    }
    }""" % HASHTAG)


# it doesn't seem like we need any other fields yet
# I'll add them as we go on if needed
USER_INFO_BLOB = """
{
  "profile_image_url": "http://a0.twimg.com/profile_images/1777569006/image1327396628_normal.png",
  "id_str": "42",
  "profile_image_url_https": "https://si0.twimg.com/profile_images/1777569006/image1327396628_normal.png",
  "id": 42,
  "screen_name": "rsarver"
}
"""


class UserModelTest(TestCase):
    def setUp(self):
        self.guy1 = User.objects.create(screen_name='guy1', twitter_id='1')
        self.guy2 = User.objects.create(screen_name='guy2', twitter_id='2')

    def tearDown(self):
        Tweet.objects.all().delete()
        User.objects.all().delete()

    @httpretty.activate
    def test_user_from_twitter_id(self):
        # I wish I knew a better way than to hardcode the URL
        httpretty.register_uri(httpretty.GET,
                               "https://api.twitter.com/1.1/users/show.json",
                               body=USER_INFO_BLOB)

        u = User.from_twitter_id('42')
        # 2 guys from setUp + a new user
        self.assertEquals(User.objects.count(), 3)
        self.assertEquals(u.screen_name, 'rsarver')
        # let's ignore the protocol for now since we might want https later
        self.assertTrue(u.avatar.endswith(
            'twimg.com/profile_images/1777569006/image1327396628_normal.png')
        )

    def test_get_limit_usage(self):
        # testing without a receiver
        usage = self.guy1.get_limit_usage()
        self.assertEquals(usage['per_week'], 0)
        self.assertNotIn('per_week_receiver', usage)

        # testing with a receiver
        usage = self.guy1.get_limit_usage(self.guy2)
        self.assertEquals(usage['per_week'], 0)
        self.assertEquals(usage['per_week_receiver'], 0)

        Tweet.objects.create(twitter_id='123', amount=5, sender=self.guy1,
                             receiver=self.guy2, date=datetime.now())

        # testing with a correct receiver
        usage = self.guy1.get_limit_usage(self.guy2)
        self.assertEquals(usage['per_week'], 5)
        self.assertEquals(usage['per_week_receiver'], 5)

        # testing with an incorrect receiver
        # of course, one cannot send karma to himself,
        # but that'll only helps
        usage = self.guy1.get_limit_usage(self.guy1)
        self.assertEquals(usage['per_week'], 5)
        self.assertEquals(usage['per_week_receiver'], 0)

    @httpretty.activate
    def test_renames_on_screen_name_clash(self):
        info_blob = """
        {
        "profile_image_url":
            "http://a0.twimg.com/profile_images/1777569006/image1327396628_normal.png",
        "id_str": "1",
        "profile_image_url_https":
            "https://si0.twimg.com/profile_images/1777569006/image1327396628_normal.png",
        "id": 1,
        "screen_name": "donkey"
        }
        """

        # guy1 renames himself to `donkey`
        httpretty.register_uri(httpretty.GET,
                               'https://api.twitter.com/1.1/users/show.json',
                               body=info_blob)

        # a new user named `guy1` appears
        u = User(screen_name='guy1', twitter_id='42')
        u.save()

        prev_guy1 = User.objects.get(twitter_id='1')

        # guy1 is renamed to donkey
        self.assertEquals(prev_guy1.screen_name, 'donkey')

    @httpretty.activate
    def test_deletes_on_screen_name_clash_if_404(self):
        # original guy 1 doesn't exist anymore
        httpretty.register_uri(httpretty.GET,
                               'https://api.twitter.com/1.1/users/show.json',
                               status=404)

        # a new user named `guy1` appears
        u = User(screen_name='guy1', twitter_id='42')
        u.save()

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(twitter_id='1')

    def test_get_position(self):
        Tweet(receiver=self.guy1, sender=self.guy2, twitter_id='1',
              amount=5, date=datetime.now()).save()
        Tweet(receiver=self.guy2, sender=self.guy1, twitter_id='1',
              amount=1, date=datetime.now()).save()

        self.assertEquals(self.guy1.get_position(), 1)
        self.assertEquals(self.guy2.get_position(), 2)

class TweetModelTest(TestCase):
    def setUp(self):
        self.guy1 = User.objects.create(screen_name='guy1', twitter_id='1')
        self.guy2 = User.objects.create(screen_name='guy2', twitter_id='2')

    def tearDown(self):
        User.objects.all().delete()

    def test_receiver_banned(self):
        # ban him
        self.guy1.banned = True
        self.guy1.save()

        t = Tweet(amount=5, twitter_id='42', receiver=self.guy1,
                  sender=self.guy2, date=datetime.now())
        self.assertRaises(ValidationError, t.save)

    def test_receiver_equals_sender(self):
        t = Tweet(amount=5, twitter_id='42', receiver=self.guy1,
                  sender=self.guy1, date=datetime.now())
        self.assertRaises(ValidationError, t.save)

    def test_sender_banned(self):
        self.guy2.banned = True
        self.guy2.save()

        t = Tweet(amount=5, twitter_id='42', receiver=self.guy1,
                  sender=self.guy2, date=datetime.now())
        self.assertRaises(ValidationError, t.save)

    def test_invalid_amounts(self):
        amounts = settings.UPKARMA_SETTINGS['valid_amount_range']

        t = Tweet(twitter_id='42', receiver=self.guy1,
                  sender=self.guy2, date=datetime.now())
        # not enough
        t.amount = amounts[0]-1
        self.assertRaises(ValidationError, t.save)

        # too many
        t.amount = amounts[1]+1
        self.assertRaises(ValidationError, t.save)

    def test_per_week_limit(self):
        limit = settings.UPKARMA_SETTINGS['limits']['per_week']
        max_amount = settings.UPKARMA_SETTINGS['valid_amount_range'][1]

        # we need some users
        # so we don't hit the per_week_receiver

        guys = [User.objects.create(screen_name=str(i), twitter_id=str(i))
                for i in range(limit//max_amount)]

        for i in range(limit//max_amount):
            # we fill up the per week limit
            t = Tweet(amount=max_amount, twitter_id=str(i),
                      sender=self.guy1, receiver=guys[i],
                      date=datetime.now())
            t.save()

        t = Tweet(amount=max_amount, twitter_id='42',
                  sender=self.guy1, receiver=self.guy2,
                  date=datetime.now())
        self.assertRaises(ValidationError, t.save)

    def test_per_week_receiver_limit(self):
        limit = settings.UPKARMA_SETTINGS['limits']['per_week_receiver']
        max_amount = settings.UPKARMA_SETTINGS['valid_amount_range'][1]

        for i in range(limit//max_amount):
            t = Tweet(amount=max_amount, twitter_id=str(i),
                      sender=self.guy1, receiver=self.guy2,
                      date=datetime.now())
            t.save()

        t = Tweet(amount=max_amount, twitter_id='42',
                  sender=self.guy1, receiver=self.guy2,
                  date=datetime.now())
        self.assertRaises(ValidationError, t.save)



class TweetbackTest(TestCase):
    @httpretty.activate
    def test_tweets_back(self):
        httpretty.register_uri(httpretty.POST,
                               'https://api.twitter.com/1.1/statuses/update.json',
                               body=json.dumps('{}'))

        t = get_base_tweet()
        tweetback("You're a wizard, Harry", t)

        self.assertEquals(get_req_arg('status'), "@guy1 You're a wizard, Harry")
        self.assertEquals(get_req_arg('in_reply_to_status_id'), str(t['id']))

class CachedDecoratorTest(TestCase):
    def setUp(self):
        self.patcher = patch('karma.utils.cache')
        self.cache_mock = self.patcher.start()

        def func(*args, **kwargs):
            return [1,2,3]

        self.func = func

    def test_cache_empty(self):
        func = cached('this-is-a-key')(self.func)

        # cache is empty
        self.cache_mock.get.return_value = None

        self.assertEquals(func(), [1,2,3])
        self.cache_mock.get.assert_called_with('this-is-a-key')
        self.cache_mock.set.assert_called_with('this-is-a-key', [1,2,3], None)

    def test_cache_not_empty(self):
        func = cached('this-is-a-key')(self.func)

        # there's a result in cache
        self.cache_mock.get.return_value = [1,2,3]

        self.assertEquals(func(), [1,2,3])
        self.cache_mock.get.assert_called_with('this-is-a-key')
        # set() shouldn't be called when
        # the result is retrieved from cache
        self.assertFalse(self.cache_mock.set.called)

    def test_key_format(self):
        # so set() is called as well
        self.cache_mock.get.return_value = None

        func = cached('key:{0}:{k}')(self.func)
        expected_key = 'key:pos:kw'

        func('pos', k='kw')

        self.cache_mock.get.assert_called_with('key:pos:kw')
        self.cache_mock.set.assert_called_with('key:pos:kw', [1,2,3], None)

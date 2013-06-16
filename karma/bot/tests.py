import json
from mock import Mock

from django.test import TestCase

from .core import process_tweet
from ..models import User
from ..exceptions import BadFormat

def get_base_tweet():
    # this is a tweet template
    # we replace some values for each test
    return json.loads("""
    {
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
    "text": "#upkarma 5 @guy2",
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
    }""")


class BotFormatHandlingTest(TestCase):
    def test_bot_fails_on_missing_amount(self):
        t = get_base_tweet()
        t['text'] = '#upkarma @guy2'
        self.assertRaises(BadFormat, process_tweet, t)

    def test_bot_fails_on_no_mentions(self):
        t = get_base_tweet()
        t['text'] = '#upkarma 1'
        t['entities']['user_mentions'] = []
        self.assertRaises(BadFormat, process_tweet, t)

    def test_bot_fails_on_too_many_mentions(self):
        t = get_base_tweet()
        t['text'] = '#upkarma 1 @abc @def #ghi'
        mention = {"name":"Twitter API", "indices":[4,15],
                   "screen_name":"twitterapi", "id":6253282,
                   "id_str":"6253282"}

        t['entities']['user_mentions'].append(mention)
        t['entities']['user_mentions'].append(mention)
        t['entities']['user_mentions'].append(mention)

        self.assertRaises(BadFormat, process_tweet, t)

class BotUserFindingTest(TestCase):
    def setUp(self):
        User.objects.create(screen_name='guy1', twitter_id='1')
        User.objects.create(screen_name='guy2', twitter_id='2')

    def tearDown(self):
        User.objects.all().delete()

    def test_non_existant_sender(self):
        t = get_base_tweet()
        t['user']['id_str'] = '42'
        self.assertRaises(User.DoesNotExist, process_tweet, t)

    def test_non_existant_receiver(self):
        """
        from_twitter_id should be called when a receiver doesn't exist
        """
        mock = Mock()
        User.from_twitter_id = mock

        t = get_base_tweet()
        t['entities']['user_mentions'][0]['screen_name'] = 'guy3'
        t['entities']['user_mentions'][0]['id_str'] = '3'
        t['entities']['user_mentions'][0]['id'] = 3

        process_tweet(t)
        self.assertTrue(mock.called)

import httpretty

from django.test import TestCase
from django.core.exceptions import ValidationError

from .models import Tweet, User


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
            '://a0.twimg.com/profile_images/1777569006/image1327396628_normal.png')
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
                             receiver=self.guy2)

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



class TweetModelTest(TestCase):
    def setUp(self):
        self.guy1 = User.objects.create(screen_name='guy1', twitter_id='1',
                banned=True)
        self.guy2 = User.objects.create(screen_name='guy2', twitter_id='2')

    def tearDown(self):
        User.objects.all().delete()

    def test_receiver_banned(self):
        t = Tweet(amount=5, twitter_id='42', receiver=self.guy1,
                sender=self.guy2)
        self.assertRaises(ValidationError, t.save)

    def test_sender_banned(self):
        t = Tweet(amount=5, twitter_id='42', receiver=self.guy2,
                sender=self.guy1)
        self.assertRaises(ValidationError, t.save)

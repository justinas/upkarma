"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from .models import Tweet, User

import httpretty

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
    @httpretty.activate
    def test_user_from_twitter_id(self):
        # I wish I knew a better way than to hardcode the URL
        httpretty.register_uri(httpretty.GET,
                               "https://api.twitter.com/1.1/users/show.json",
                               body=USER_INFO_BLOB)

        u = User.from_twitter_id('42')
        self.assertEquals(User.objects.count(), 1)
        self.assertEquals(u.screen_name, 'rsarver')
        # let's ignore the protocol for now since we might want https later
        self.assertTrue(u.avatar.endswith(
            '://a0.twimg.com/profile_images/1777569006/image1327396628_normal.png')
        )

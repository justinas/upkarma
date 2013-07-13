from karma.models import User

class TwitterBackend(object):
    """
    A backend that finds a user by twitter_id
    and authenticates them, no questions asked.
    """

    def authenticate(self, twitter_id=None):
        return self.get_user(twitter_id)

    def get_user(self, twitter_id=None):
        try:
            return User.objects.get(twitter_id=twitter_id)
        except User.DoesNotExist:
            return None

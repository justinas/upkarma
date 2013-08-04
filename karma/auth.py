from karma.models import User

class TwitterBackend(object):
    """
    A backend that finds a user by twitter_id
    and authenticates them, no questions asked.
    """

    def authenticate(self, twitter_id=None):
        try:
            return User.objects.get(twitter_id=twitter_id)
        except User.DoesNotExist:
            return None

    def get_user(self, pk=None):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

from django.db import models
from django.db.models import Sum

from karma.utils import get_week_start

class UserManager(models.Manager):
    def most_loved_users(self, user):
        """
        Returns a queryset with users
        that received the most points
        from `user`
        """
        qs = self.get_query_set()
        # get users that received karma from `user`
        qs = qs.filter(karma_receives__sender=user)
        # sum the points they received
        qs = qs.annotate(points=Sum('karma_receives__amount'))
        # order
        qs = qs.order_by('-points')

        return qs

    def most_loved_by(self, user):
        """
        Returns a queryset with users
        that sent the most points
        from `user`
        """
        qs = self.get_query_set()
        # get users that sent karma to `user`
        qs = qs.filter(karma_sends__receiver=user)
        # sum the points
        qs = qs.annotate(points=Sum('karma_sends__amount'))
        # order
        qs = qs.order_by('-points')

        return qs

    def sends_this_week(self, user):
        """
        Returns a summary of points sent this week,
        grouped by user.

        It essentially helps user to see
        their own limit usage
        """

        # django fucks up with annotations + filtering + stuff
        # so we're using raw here

        query = """SELECT u.*, SUM(t.amount) AS points
        FROM karma_user u
        JOIN karma_tweet t
        ON t.receiver_id = u.id
        WHERE t.sender_id = %s
        AND t.date >= %s
        GROUP BY u.id
        ORDER BY points DESC
        """

        qs = self.raw(query, [user.id, get_week_start()])

        return list(qs)

    def with_points(self):
        qs = self.get_query_set()
        return qs.annotate(points=Sum('karma_receives__amount'))

    def with_points_sent(self):
        qs = self.get_query_set()
        return qs.annotate(points=Sum('karma_sends__amount'))

    def top(self):
        qs = self.with_points().exclude(banned=True)
        return qs.order_by('-points').exclude(points=None)

    def top_sent(self):
        qs = self.with_points_sent().exclude(banned=True)
        return qs.order_by('-points').exclude(points=None)

class PublicUserManager(UserManager):
    """
    This is the manager that gets exposed to the public.
    While `UserManager` is suitable for internal work,
    `PublicUserManager` should be used in views, API, etc.
    """
    def get_query_set(self):
        qs = super(PublicUserManager, self).get_query_set()
        # do not return banned users
        return qs.filter(banned=False)

class PublicTweetManager(models.Manager):
    def get_query_set(self):
        """
        Replicates the filters done
        by PublicUserManager
        """
        qs = super(PublicTweetManager, self).get_query_set()
        return qs.filter(receiver__banned=False, sender__banned=False)

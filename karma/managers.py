from django.db import models
from django.db.models import Sum

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

    def with_points(self):
        qs = self.get_query_set()
        return qs.annotate(points=Sum('karma_receives__amount'))

    def with_points_sent(self):
        qs = self.get_query_set()
        return qs.annotate(points_sent=Sum('karma_sends__amount'))

    def top(self):
        qs = self.with_points().exclude(banned=True)
        return qs.order_by('-points').exclude(points=None)

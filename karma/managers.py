from django.db import models
from django.db.models import Sum

class UserManager(models.Manager):
    def with_points(self):
        qs = self.get_query_set()
        return qs.annotate(points=Sum('karma_receives__amount'))

    def with_points_sent(self):
        qs = self.get_query_set()
        return qs.annotate(points_sent=Sum('karma_sends__amount'))


    def top(self):
        qs = self.with_points()
        return qs.order_by('-points').exclude(points=None)

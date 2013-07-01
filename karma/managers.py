from django.db import models
from django.db.models import Sum
from django.db.models.query import QuerySet

class UserQuerySet(QuerySet):
    def with_points(self):
        return self.annotate(points=Sum('karma_receives__amount'))

    def with_points_sent(self):
        return self.annotate(points_sent=Sum('karma_sends__amount'))

class UserManager(models.Manager):
    def get_query_set(self):
        return UserQuerySet(self.model)

    def top(self):
        qs = self.get_query_set()
        qs = qs.with_points().exclude(banned=True)
        return qs.order_by('-points').exclude(points=None)

from datetime import datetime

from django.db import connection
from django.db.models import Sum, Count

from .models import User, Tweet

def total_points():
    """
    Returns the total amount
    of points sent
    """
    return Tweet.objects.all().aggregate(s=Sum('amount'))['s']

def total_times_sent():
    """
    Returns the total number of
    times points have been sent
    """
    return Tweet.objects.all().aggregate(s=Count('amount'))['s']

def minutes_between_sends():
    try:
        first = Tweet.objects.all()[0]
        last = Tweet.objects.all().order_by('-pk')[0]
    except IndexError:
        return 0

    delta = last.date - first.date
    minutes = delta.total_seconds()/60

    return minutes / total_times_sent()

def all_stats():
    results = {}
    results['total_points'] = total_points()
    results['total_times_sent'] = total_times_sent()
    # average amount per send
    results['avg_per_send'] = (float(results['total_points']) /
                               results['total_times_sent'])
    results['minutes_between_sends'] = minutes_between_sends()

    return results

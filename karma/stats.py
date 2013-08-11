from datetime import datetime

from django.db import connection
from django.db.models import Sum, Count

from .models import User, Tweet

def total_points():
    """
    Returns the total amount
    of points sent
    """
    return Tweet.objects.all().aggregate(s=Sum('amount'))['s'] or 0

def total_times_sent():
    """
    Returns the total number of
    times points have been sent
    """
    return Tweet.objects.all().aggregate(s=Count('amount'))['s'] or 0

def minutes_between_sends():
    try:
        first = Tweet.objects.all()[0]
        last = Tweet.objects.all().order_by('-pk')[0]
    except IndexError:
        return 0

    delta = last.date - first.date
    minutes = delta.total_seconds()/60

    return minutes / total_times_sent()

def amount_by_dow():
    """
    Returns a list of (dow, amount) tuples
    where `dow` is the day of week (1 to 7, Mon to Sun)
    and `amount` is the amount of karma sent on that dow
    """
    query = """
    SELECT
    EXTRACT(isodow FROM "date")::int as "dow",
    SUM(amount) as amount
    FROM karma_tweet
    GROUP BY dow
    ORDER BY dow ASC
    """

    cursor = connection.cursor()
    cursor.execute(query)

    return cursor.fetchall()

def amount_by_month():
    """
    Does the same as `amount_by_dow()`, except for months.
    """

    query = """
    SELECT
    EXTRACT(month FROM "date")::int as "month",
    SUM(amount) as amount
    FROM karma_tweet
    GROUP BY month
    ORDER BY month ASC
    """

    cursor = connection.cursor()
    cursor.execute(query)

    return cursor.fetchall()


def all_stats():
    results = {}
    results['total_points'] = total_points()
    results['total_times_sent'] = total_times_sent()
    # average amount per send
    try:
        results['avg_per_send'] = (float(results['total_points']) /
                               results['total_times_sent'])
    except ZeroDivisionError:
        results['avg_per_send'] = 0.0
    results['minutes_between_sends'] = minutes_between_sends()

    # for graphs
    results['amount_by_dow'] = amount_by_dow()
    results['amount_by_month'] = amount_by_month()

    return results

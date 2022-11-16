# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django.db.models import Sum
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import json

from karma.models import User
from karma.stats import all_stats
from karma.utils import cached, ym_to_js_timestamp, get_week_start

PER_PAGE = 50
SEARCH_PER_PAGE = 30

def index(request, page_number=1):
    top = User.objects.top()
    paginator = Paginator(top, PER_PAGE)

    try:
        page = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        return HttpResponseRedirect(reverse('karma.views.index'))

    context = dict(user_top=page.object_list, page=page,
                   active_page='index')


    return render(request, 'karma/index.html', context)

def get_user_context(name):
    try:
        qs = User.objects.exclude(banned=True)

        user = qs.get(screen_name__iexact=name)
        points = user.karma_receives.aggregate(s=Sum('amount'))['s'] or 0
        points_sent = user.karma_sends.aggregate(s=Sum('amount'))['s'] or 0
        monthly_history = [
            (ym_to_js_timestamp(i[0]), i[1])
            for i in user.get_monthly_point_history()
        ]
        most_loved_users = User.objects.most_loved_users(user)[0:5]
        most_loved_by = User.objects.most_loved_by(user)[0:5]

        sends_this_week = User.objects.sends_this_week(user)
        # WARNING: INCONSISTENCY (User objects vs. dict)!
        sends_this_week.append({'points' : sum(u.points for u in sends_this_week)})

    except User.DoesNotExist:
        raise Http404()

    return dict(user=user, points=points, points_sent=points_sent,
                monthly_history=json.dumps(monthly_history),
                most_loved_users=most_loved_users,
                most_loved_by=most_loved_by,
                sends_this_week=sends_this_week)

def user(request, name):
    context = get_user_context(name)
    return render(request, 'karma/user.html', context)

def stats(request):
    context = all_stats()

    context['amount_by_month'] = json.dumps(context['amount_by_month'])
    context['amount_by_dow'] = json.dumps(context['amount_by_dow'])

    context['active_page'] = 'stats'

    return render(request, 'karma/stats.html', context)

def search(request):
    try:
        query = request.GET['q']
    except KeyError:
        return render(request, 'karma/search_results.html')

    qs = User.objects.filter(screen_name__icontains=query)

    if len(qs) == 1:
        return HttpResponseRedirect(reverse('user',
                                            args=(qs[0].screen_name,)))

    paginator = Paginator(qs, SEARCH_PER_PAGE)

    try:
        page_number = request.GET.get('page', 1)
        page = paginator.page(page_number)

    except EmptyPage:
        if page_number == 1:
            pass
        else:
            return HttpResponseRedirect(reverse('karma.views.index'))

    except PageNotAnInteger:
        return HttpResponseRedirect(reverse('karma.views.index'))

    # group these in pairs
    page.object_list = [page.object_list[i:i+2]
                        for i in range(0, len(page.object_list), 2)]
    context = dict(page=page, results=qs, query=query)

    return render(request, 'karma/search_results.html', context)

def guide(request):
    context = {}
    context['active_page'] = 'guide'

    return render(request, 'karma/guide.html', context)

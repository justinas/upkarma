# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404
from django.db.models import Sum
import json

from karma.models import User
from karma.utils import cached, ym_to_js_timestamp

def index(request):
    top = User.objects.top()[0:20]

    return render_to_response('karma/index.html', {'user_top' : top})

def get_user_context(name):
    try:
        qs = User.objects.exclude(banned=True)

        user = qs.get(screen_name__iexact=name)
        points = user.karma_receives.aggregate(s=Sum('amount'))['s']
        points_sent = user.karma_sends.aggregate(s=Sum('amount'))['s']
        monthly_history = [
            (ym_to_js_timestamp(i[0]), i[1])
            for i in user.get_monthly_point_history()
        ]

    except User.DoesNotExist:
        raise Http404()

    return dict(user=user, points=points, points_sent=points_sent,
                monthly_history=json.dumps(monthly_history))

def user(request, name):
    context = get_user_context(name)
    return render_to_response('karma/user.html', context)

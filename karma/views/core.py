# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404
from django.db.models import Sum

from karma.models import User
from karma.utils import cached

def index(request):
    top = User.objects.top()[0:20]

    return render_to_response('karma/index.html', {'user_top' : top})

def get_full_user(name):
    try:
        qs = User.objects.exclude(banned=True)
        user = qs.get(screen_name__iexact=name)
        points = user.karma_receives.aggregate(s=Sum('amount'))['s']
        points_sent = user.karma_sends.aggregate(s=Sum('amount'))['s']

    except User.DoesNotExist:
        raise Http404()

    return dict(user=user, points=points, points_sent=points_sent)

def user(request, name):
    context = get_full_user(name)
    return render_to_response('karma/user.html', context)

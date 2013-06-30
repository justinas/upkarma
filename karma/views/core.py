# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404

from karma.models import User

def index(request):
    top = User.objects.top()[0:20]

    return render_to_response('karma/index.html', {'user_top' : top})

def user(request, name):
    user = get_object_or_404(User, screen_name__iexact=name)

    return render_to_response('karma/user.html', {'user' : user})

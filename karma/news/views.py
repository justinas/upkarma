# Create your views here.
from django.shortcuts import render
from .models import Entry

def news_list(request):
    entries = Entry.public.all()

    context = dict(entries=entries)
    context['active_page'] = 'news'
    return render(request, 'karma/news_list.html', context)

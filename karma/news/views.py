# Create your views here.
from django.shortcuts import render
from .models import Entry

def news_list(request):
    entries = Entry.public.all()

    context = dict(entries=entries)

    return render(request, 'karma/news_list.html', context)

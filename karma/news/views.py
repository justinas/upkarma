# Create your views here.
from django.shortcuts import render, get_object_or_404
from .models import Entry

def news_list(request):
    entries = Entry.public.all()

    context = dict(entries=entries)
    context['active_page'] = 'news'
    return render(request, 'karma/news_list.html', context)

def news_single(request, pk):
    entry = get_object_or_404(Entry.public, pk=pk)

    context = dict(entry=entry)
    context['active_page'] = 'news'
    return render(request, 'karma/news_single.html', context)

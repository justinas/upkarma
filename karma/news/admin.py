from django.contrib import admin
from .models import Entry

class EntryAdmin(admin.ModelAdmin):
    exclude = ('text_rendered',)

admin.site.register(Entry, EntryAdmin)

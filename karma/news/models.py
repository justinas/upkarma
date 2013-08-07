from django.db import models
from django.conf import settings

# text formats
HTML = 0
MARKDOWN = 1

class Entry(models.Model):
    title = models.CharField(max_length=255, blank=False)

    text = models.TextField()
    text_rendered = models.TextField()

    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    date = models.DateTimeField()
    published = models.BooleanField(default=False)

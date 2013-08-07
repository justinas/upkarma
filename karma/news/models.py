from django.db import models
from django.conf import settings

import markdown

# text formats
HTML = 0
MARKDOWN = 1

# default to markdown
FORMAT = getattr(settings, 'KARMA_NEWS_FORMAT', 1)

class Entry(models.Model):
    title = models.CharField(max_length=255, blank=False)

    text = models.TextField()
    text_rendered = models.TextField()

    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    date = models.DateTimeField()
    published = models.BooleanField(default=False)

    def save(self, **kwargs):
        if FORMAT == HTML:
            pass # do nothing, it
        elif FORMAT == MARKDOWN:
            self.text_rendered = markdown.markdown(self.text)

        super(Entry, self).save()

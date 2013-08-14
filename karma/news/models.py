from django.db import models
from django.conf import settings

from datetime import datetime
import markdown2 as markdown

# text formats
HTML = 0
MARKDOWN = 1

# default to markdown

class PublicEntryManager(models.Manager):
    def get_query_set(self):
        qs = super(PublicEntryManager, self).get_query_set()
        # only published entries from the past
        qs = qs.filter(published=True, date__lte=datetime.now())
        # order by date DESC
        qs = qs.order_by('-date')

        return qs

class Entry(models.Model):
    title = models.CharField(max_length=255, blank=False)

    text = models.TextField()
    text_rendered = models.TextField()

    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    date = models.DateTimeField()
    published = models.BooleanField(default=False)

    # managers
    objects = models.Manager()
    public = PublicEntryManager()

    def save(self, **kwargs):
        fmt = getattr(settings, 'KARMA_NEWS_FORMAT', 1)
        if fmt == HTML:
            self.text_rendered = self.text
        elif fmt == MARKDOWN:
            self.text_rendered = markdown.markdown(self.text)

        super(Entry, self).save()

    def __unicode__(self):
        return u'{0} (published: {1})'.format(self.title, self.published)

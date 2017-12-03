"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from datetime import datetime, timedelta
import factory

from karma.models import User
from .models import Entry, HTML, MARKDOWN

class EntryFactory(factory.Factory):
    FACTORY_FOR = Entry

    published = True
    # always in the past
    date = factory.LazyAttribute(lambda _: datetime.now() - timedelta(days=1))

class NewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(twitter_id='1')

    def test_html_rendering(self):
        with self.settings(KARMA_NEWS_FORMAT=HTML):
            entry = EntryFactory.create(author=self.user, title=' ')
            entry.text = '**not weak**'
            entry.save()
            self.assertEqual(entry.text_rendered, entry.text)

    def test_markdown_rendering(self):
        with self.settings(KARMA_NEWS_FORMAT=MARKDOWN):
            entry = EntryFactory.create(author=self.user, title=' ')
            entry.text = '**not weak**'
            entry.save()
            self.assertEqual(entry.text_rendered.strip(),
                          """<p><strong>not weak</strong></p>""")

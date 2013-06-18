import json
import logging
from karma.models import User, Tweet
from datetime import datetime

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'

log = logging.getLogger('karma.importer')

def import_from_dump(blob, silent=False):
    """Takes a JSON blob from a dumpdata file from the old upkarma
    and imports the Tweets and Users from that"""
    objects = json.loads(blob)
    log.info('Import started')
    for obj in objects:
        if obj['model'] == 'karma.user':
            u = User()
            u.screen_name = obj['fields']['username']
            u.twitter_id = obj['fields']['twitter_id']
            u.banned = obj['fields']['banned']
            u.pk = obj['pk']
            u.save()
            log.info('{0} saved'.format(u))

        elif obj['model'] == 'karma.tweet':
            if obj['fields']['text'].startswith('RT @'):
                continue # skip retweets
            log.info('Skipping Tweet id {0} due to being a retweet'.format(
                obj['pk'])
            )

            t = Tweet()
            t.amount = obj['fields']['amount']
            t.receiver = User.objects.get(pk=obj['fields']['receiver'])
            t.sender = User.objects.get(pk=obj['fields']['sender'])
            t.text = obj['fields']['text']
            t.twitter_id = obj['fields']['twitter_id']
            t.pk = obj['pk']
            t.save()
            # got to save again due to auto_now_add
            # overriding the explicit value of the field
            t.date = datetime.strptime(obj['fields']['date'], DATE_FORMAT)
            t.save()
            log.info('{0} saved'.format(t))

        else:
            raise AssertionError("This shouldn't happen")

    log.info('Import finished')

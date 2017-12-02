import json
import logging

from django.core.management.color import no_style
from django.db import connection
from django.db import transaction
from django.utils.timezone import utc

from karma.models import User, Tweet
from datetime import datetime

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'

log = logging.getLogger('karma.importer')

@transaction.atomic
def import_from_dump(blob, silent=False):
    """Takes a JSON blob from a dumpdata file from the old upkarma
    and imports the Tweets and Users from that"""
    objects = json.loads(blob)
    log.info('Import started')
    for obj in objects:
        if obj['model'] == 'karma.user':
            u = User()
            u.avatar = obj['fields']['avatar']
            u.screen_name = obj['fields']['username']
            u.twitter_id = obj['fields']['twitter_id']
            u.banned = obj['fields']['banned']
            u.pk = obj['pk']
            u.save()
            log.info('{0} saved'.format(u))

        elif obj['model'] == 'karma.tweet':
            if obj['fields']['text'].startswith('RT @'):
                log.info('Skipping Tweet id {0} due to being a retweet'.format(
                    obj['pk'])
                )
                continue # skip retweets

            t = Tweet()
            t.amount = obj['fields']['amount']
            t.receiver = User.objects.get(pk=obj['fields']['receiver'])
            t.sender = User.objects.get(pk=obj['fields']['sender'])
            t.text = obj['fields']['text']
            t.twitter_id = obj['fields']['twitter_id']
            t.pk = obj['pk']

            date = datetime.strptime(obj['fields']['date'], DATE_FORMAT)
            t.date = date.replace(tzinfo=utc)

            t.save(skip_checks=True)
            log.info('{0} saved'.format(t))

        else:
            raise AssertionError("This shouldn't happen")

    # fast-forward sequences to start at max(id)
    # based on loaddata
    sql = connection.ops.sequence_reset_sql(no_style(), [Tweet, User])
    cursor = connection.cursor()

    for line in sql:
        cursor.execute(line)

    cursor.close()

    log.info('Import finished')

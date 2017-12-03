from django.core.management.base import BaseCommand, CommandError
import logging
import traceback
import sys

from karma.utils import get_global_client
from karma.models import User

class Command(BaseCommand):
    def handle(self, *args, **options):
        log = self.log = logging.getLogger('karma.other')

        try:
            log.debug('update_avatars starting')
            self.update_avatars()
        except KeyboardInterrupt:
            sys.exit(0)
        except BaseException as e:
            tb = traceback.format_exc()
            log.error('start_bot shutting down because of an exception\n'+tb)
            sys.exit(1)

    def update_avatars(self):
        log = self.log

        tw = get_global_client()
        users = list(User.objects.all())
        l = len(users)
        while users:
            part = users[0:100]
            ids = ','.join(u.twitter_id for u in part)
            info = tw.users.lookup(user_id=ids)
            for u in info:
                entry = User.objects.filter(twitter_id=u['id_str'])
                entry.update(avatar=u['profile_image_url_https'])

            users = users[100:]
        log.debug("Updated avatars for {0} users".format(l))

from django.core.management.base import BaseCommand, CommandError
import logging
import traceback
import sys

from karma.bot import Bot
from karma.utils import get_redis_client

class Command(BaseCommand):
    def handle(self, *args, **options):
        log = logging.getLogger('karma.bot')

        red = get_redis_client()
        max_id = red.get('max_id')

        if not max_id:
            raise CommandError('max_id is not set')

        bot = Bot()
        try:
            log.debug(u'start_bot starting')
            bot.run(max_id)
        except KeyboardInterrupt:
            sys.exit(0)
        except BaseException as e:
            tb = traceback.format_exc()
            log.error(u'start_bot shutting down because of an exception\n'+tb)
            sys.exit(1)

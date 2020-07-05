from django.core.management.base import BaseCommand, CommandError
import logging
import traceback
import sys
import time

from karma.bot.core import Bot
from karma.utils import get_redis_client

class Command(BaseCommand):
    def handle(self, *args, **options):
        log = logging.getLogger('karma.bot')

        red = get_redis_client()
        max_id = red.get('max_id')

        if not max_id:
            # TODO: assume 0 instead? dangerous
            raise CommandError('max_id is not set')

        max_id = int(max_id)

        try:
            bot = Bot()
            log.debug('start_bot starting')
            bot.run(max_id)
        except KeyboardInterrupt:
            sys.exit(0)
        except BaseException as e:
            tb = traceback.format_exc()
            log.error('start_bot sleeping 10 minutes and shutting down because of an exception\n'+tb)
            # prevents respawning too fast
            time.sleep(600)
            sys.exit(1)

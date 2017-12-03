from django.core.management.base import BaseCommand, CommandError
from karma.importer.core import import_from_dump

ERROR_NO_FILENAME = "./manage.py import_karma takes one argument - " \
        "the filename of the dump produced by dumpdata"

class Command(BaseCommand):
    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError(ERROR_NO_FILENAME)
        import_from_dump(open(args[0]).read())

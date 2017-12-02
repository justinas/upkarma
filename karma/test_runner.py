import logging
from django.test.runner import DiscoverRunner

class KarmaTestRunner(DiscoverRunner):
    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        # disable all karma.* logging
        logging.disable(logging.DEBUG)

        if not test_labels:
            test_labels = ['karma', 'karma.bot', 'karma.importer',
                           'karma.stream', 'karma.news']

        super(KarmaTestRunner, self).run_tests(test_labels, extra_tests,
                                              **kwargs)

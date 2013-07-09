import logging
from django.test.simple import DjangoTestSuiteRunner

class KarmaTestRunner(DjangoTestSuiteRunner):
    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        # disable all karma.* logging
        logging.disable(logging.DEBUG)

        if not test_labels:
            test_labels = ['karma', 'bot', 'importer', 'stream']

        super(KarmaTestRunner, self).run_tests(test_labels, extra_tests,
                                              **kwargs)

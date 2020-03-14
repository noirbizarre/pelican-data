import re
import unittest

from os.path import dirname, join

from pelican import readers


RESOURCES_PATH = join(dirname(__file__), 'test-resources')

RE_EXTRACT = re.compile(r'<p>(.*?)</p>')


class TestDataContext(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        super(TestDataContext, self).setUp()

        import data
        data.register()

    def assert_in_context(self, value, context):
        pass

import sys
import unittest
import os

sys.path.append('..')
from wavefront.utils import Configuration

class TestUtils(unittest.TestCase):

    def test_get_dict(self):
        config_file_path = os.path.join(os.getcwd(), 'test-conf/test-newrelic-details.conf')
        config = Configuration(config_file_path)

        test_dict = config.getdict('wavefront-api','source_map',{})

        assert test_dict['team.test'] == ".*testregex.*"
        assert test_dict['team.test2'] == "ttregex.*"

    def test_get_dict_default(self):
        config_file_path = os.path.join(os.getcwd(), 'test-conf/test-newrelic-details.conf')
        config = Configuration(config_file_path)

        test_dict = config.getdict('wavefront-api', 'bad_source_map', {'default_key': 'default_value'})

        assert test_dict['default_key'] == "default_value"


if __name__ == '__main__':
    unittest.main()

import sys
import unittest
import re

sys.path.append('..')
from wavefront.newrelic import NewRelicMetricRetrieverCommand

class TestNewRelicCommand(unittest.TestCase):
    def test_whitelist_blacklist(self):
        fields = ['WebTransaction/GoodCall/1', 'OtherTransaction/GoodCall/1', 'WebTransaction/BadCall/1']

        whitelist = ['WebTransaction.*', 'OtherTransaction.*']
        whitelist_compiled = []
        for regex in whitelist:
            whitelist_compiled.append(re.compile(regex))

        blacklist = ['WebTransaction\/BadCall.*']
        blacklist_compiled = []
        for regex in blacklist:
            blacklist_compiled.append(re.compile(regex))

        cmd = NewRelicMetricRetrieverCommand()
        result = cmd._filter_fields_by_regex(fields, whitelist, whitelist_compiled, blacklist, blacklist_compiled)

        assert 'WebTransaction/GoodCall/1' in result
        assert 'OtherTransaction/GoodCall/1' in result
        assert 'WebTransaction/BadCall/1' not in result


if __name__ == '__main__':
    unittest.main()

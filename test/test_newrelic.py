import mock
import sys
import unittest
import re
import os
from dateutil.parser import parse

sys.path.append('..')
from wavefront.newrelic import NewRelicMetricRetrieverCommand
from wavefront.newrelic import NewRelicPluginConfiguration
from wavefront_api_client.rest import ApiException


class TestNewRelicCommand(unittest.TestCase):
    def setUp(self):
        self.start = parse('2017-03-01T00:00:00+00:00')
        self.end = parse('2017-03-01T00:10:00+00:00')
        self.app_id = 123
        self.app_name = 'test_app'


    def test_whitelist_blacklist(self):
        metric_name_1 = 'WebTransaction/GoodCall/1'
        metric_name_2 = 'OtherTransaction/GoodCall/1'
        metric_name_3 = 'WebTransaction/BadCall/1'
        fields = [metric_name_1, metric_name_2, metric_name_3]

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

    def test_send_metrics_for_application(self):
        metric_name_1 = 'WebTransaction/GoodCall/1'
        metric_name_2 = 'OtherTransaction/GoodCall/1'
        metric_name_3 = 'WebTransaction/BadCall/1'
        fields = [metric_name_1, metric_name_2, metric_name_3]

        cmd = NewRelicMetricRetrieverCommand()
        cmd.config = NewRelicPluginConfiguration(config_file_path=os.path.join(os.getcwd(), 'test-conf/test-newrelic-details.conf'))

        with mock.patch('wavefront.newrelic.NewRelicMetricRetrieverCommand.get_metrics_for_path', return_value=None) as metric_path_call, \
                mock.patch('wavefront.newrelic.NewRelicMetricRetrieverCommand.get_metric_names_for_path', return_value = fields) as metric_name_call:

            cmd.send_metrics_for_overall_application(self.app_id, self.app_name, self.start, self.end)

            assert metric_path_call.called
            assert metric_path_call.call_count == 1
            mpc_args, mpc_kwargs = metric_path_call.call_args
            assert mpc_args == ('/applications/'+ str(self.app_id),
                                [metric_name_1, metric_name_2],
                                self.start, self.end,
                                self.app_name,
                                { 'app_id': self.app_id,'app_name': self.app_name })

            assert metric_name_call.called
            assert metric_name_call.call_count == 1
            mnc_args, mnc_kwargs = metric_name_call.call_args
            assert mnc_args == ('/applications/' + str(self.app_id), [])

    def test_send_metrics_for_application_config_short_circuit(self):
        cmd = NewRelicMetricRetrieverCommand()

        cmd.config = NewRelicPluginConfiguration(
            config_file_path=os.path.join(os.getcwd(), 'test-conf/test-newrelic-details.conf'))

        cmd.config.include_application_details = False

        cmd.send_metrics_for_overall_application(self.app_id, self.app_name, self.start, self.end)

        with mock.patch('wavefront.newrelic.NewRelicMetricRetrieverCommand.get_metric_names_for_path') as metric_name_call:
            assert not metric_name_call.called


    def test_tag_source(self):
        cmd = NewRelicMetricRetrieverCommand()

        cmd.config = NewRelicPluginConfiguration(
            config_file_path=os.path.join(os.getcwd(), 'test-conf/test-newrelic-details.conf'))

        source_name = "ttregextestregex"

        with mock.patch('wavefront_api_client.SourceApi.add_source_tag') as add_source_tag_call:
            cmd.tag_source(source_name)

            assert add_source_tag_call.called
            assert add_source_tag_call.call_count == 2

    def test_tag_source_failed_attempts(self):
        cmd = NewRelicMetricRetrieverCommand()

        cmd.config = NewRelicPluginConfiguration(
            config_file_path=os.path.join(os.getcwd(), 'test-conf/test-newrelic-details.conf'))

        source_name = "ttregextestregex"

        with mock.patch('wavefront_api_client.SourceApi.add_source_tag', side_effect=ApiException) as add_source_tag_call:
            cmd.tag_source(source_name)

            assert add_source_tag_call.called
            assert add_source_tag_call.call_count == 6

    def tearDown(self):
        self.start = None
        self.end = None
        self.app_id = None
        self.app_name = None

if __name__ == '__main__':
    unittest.main()

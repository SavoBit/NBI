import json

from service.tests.functional import MonitoringTestCase


class TestFlow(MonitoringTestCase):
    ENDPOINT = '/nbi/monitoring/api/flow/measurements/'

    FLOW_ID = '4EEB5773'
    DIMENSION_NAME = 'avg_pkt_count'
    START_TIME = '2018-01-01'
    END_TIME = '2020-12-31'

    def test_flow_metric(self):
        """
        Test that validates the user can collect flow metrics.
        It asserts the response code 200 and the body
            measurements
                value
                timestamp
                value_meta
            links
        :return:
        """
        endpoint = '{}/{}/{}?start_time={}&end_time={}'.format(TestFlow.ENDPOINT, TestFlow.FLOW_ID,
                                                               TestFlow.DIMENSION_NAME, TestFlow.START_TIME,
                                                               TestFlow.END_TIME)

        result = self.app.get(endpoint, headers={'X-Auth-Token': self.cloud_admin})
        self.assertTrue(result.status, 200)

        data = json.loads(result.body.decode('utf-8'))
        for field in ['links', 'measurements']:
            self.assertTrue(field in data)

        data = data.get('measurements')[0]
        for field in ['value', 'timestamp', 'value_meta']:
            self.assertTrue(field in data)

    def test_flow_metric_unauth(self):
        """
        Test that validates an unauthenticated user can't access the measurements
        It asserts the response code 401
        :return:
        """
        endpoint = '{}/{}/{}?start_time={}&end_time={}'.format(TestFlow.ENDPOINT, TestFlow.FLOW_ID,
                                                               TestFlow.DIMENSION_NAME, TestFlow.START_TIME,
                                                               TestFlow.END_TIME)

        result = self.app.get(endpoint, headers={'X-Auth-Token': self.cloud_admin}, status=401)
        self.assertTrue(result.status, 401)

    def test_flow_invalid(self):
        """
        Test that validates the user can't collect a non existent measurement
        It asserts the response code 404
        :return:
        """
        endpoint = '{}/{}/{}?start_time={}&end_time={}'.format(TestFlow.ENDPOINT, '000000',
                                                               TestFlow.DIMENSION_NAME, TestFlow.START_TIME,
                                                               TestFlow.END_TIME)
        result = self.app.get(endpoint, headers={'X-Auth-Token': self.cloud_admin}, status=404)
        self.assertTrue(result.status, 404)

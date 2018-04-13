import json

from service.tests.functional import MonitoringTestCase


class TestAlarm(MonitoringTestCase):
    ENDPOINT = '/nbi/monitoring/api/alarms/'

    def test_get_alarms(self):
        """
        Test that validates getting all alarms
        It asserts the response code 200, the default alarm limit 5 and the fields in an alarm:
            metrics
            state
            alarm_definition
            updated_timestamp
            created_timestamp
            state_updated_timestamp
            id
        :return:
        """
        result = self.app.get(TestAlarm.ENDPOINT, headers={'X-Auth-Token': self.cloud_admin})
        self.assertEqual(result.status, 200)
        data = json.loads(result.body.decode('utf-8'))
        self.assertTrue('alarms' in data)
        for alarm in data.get('alarms'):
            for field in ['metrics', 'state', 'alarm_definition', 'updated_timestamp', 'created_timestamp',
                          'state_updated_timestamp', 'id']:
                self.assertTrue(field in alarm)
        self.assertTrue(len(data.get('alarms')) <= 5)

    def test_get_alarms_filter(self):
        """
        Test that validates getting an alarm using a filter
        It asserts the response code 200, the filtered information and the limit
        :return:
        """
        result = self.app.get(TestAlarm.ENDPOINT, headers={'X-Auth-Token': self.cloud_admin},
                              params={'limit': 2, 'state': 'OK'})

        self.assertTrue(result.status, 200)
        data = json.loads(result.body.decode('utf-8'))
        self.assertTrue('alarms' in data)
        for alarm in data.get('alarms'):
            self.assertTrue(alarm.get('state'), 'OK')
        self.assertTrue(len(data.get('alarms')) <= 2)

    def test_get_alarms_unauth(self):
        """
        Test that validates an unauthenticated user can't access the alarms
        It asserts the response code 401
        :return:
        """
        result = self.app.get(TestAlarm.ENDPOINT, params={'limit': 2, 'state': 'OK'}, status=401)
        self.assertTrue(result.status, 401)

    def test_specific_alarm(self):
        """
        Test that validates getting a specific alarm
        It asserts the response code 200 and the fields in the alarm:
            metrics
            state
            alarm_definition
            updated_timestamp
            created_timestamp
            state_updated_timestamp
            id
        :return:
        """
        result = self.app.get(TestAlarm.ENDPOINT + '000072da-53f7-434e-8d89-77c4b77f1636',
                              headers={'X-Auth-Token': self.cloud_admin})
        self.assertTrue(result.status, 200)
        data = json.loads(result.body.decode('utf-8'))
        for field in ['metrics', 'state', 'alarm_definition', 'updated_timestamp', 'created_timestamp',
                      'state_updated_timestamp', 'id']:
            self.assertTrue(field in data)

    def test_get_invalid_alarm(self):
        """
        Test that validates a user can't collect an invalid alarm id
        It asserts the response code 404
        :return:
        """
        result = self.app.get(TestAlarm.ENDPOINT + '000210ee', status=404,
                              headers={'X-Auth-Token': self.cloud_admin})
        self.assertEqual(result.status, 404)

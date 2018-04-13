import json

from service.tests.functional import MonitoringTestCase


class TestAlarmDefinition(MonitoringTestCase):
    ENDPOINT = '/nbi/monitoring/api/alarm-definitions/'

    def test_get_definition(self):
        """
        Test that validates obtaining an alarm definition
        It asserts the response code 200 and the definition body:
            expression
            deterministic
            severity
            name
            id
            actions_enabled
            match_by
            description
        :return:
        """
        endpoint = TestAlarmDefinition.ENDPOINT + 'e4478eb0-6e45-4bd4-92e5-bb1a5f0818c5'
        result = self.app.get(endpoint,
                              headers={'X-Auth-Token': self.cloud_admin})
        self.assertEqual(result.status, 200)
        data = json.loads(result.body.decode('utf-8'))
        self.assertTrue('definition' in data)
        for field in ['expression', 'deterministic', 'severity', 'name', 'id', 'actions_enabled', 'match_by',
                      'description']:
            self.assertTrue(field in data.get('definition'))

    def test_get_invalid_definition(self):
        """
        Test that validates the user can't collect a non existent definition
        It asserts the response code 404
        :return:
        """
        endpoint = TestAlarmDefinition.ENDPOINT + 'b21deac3'
        result = self.app.get(endpoint, status=404,
                              headers={'X-Auth-Token': self.cloud_admin})
        self.assertTrue(result.status, 404)

    def test_get_definition_unauth(self):
        """
        Test that validates an unauthenticated user can't access the alarm definition
        It asserts the response code 401
        :return:
        """
        endpoint = TestAlarmDefinition.ENDPOINT + 'e4478eb0-6e45-4bd4-92e5-bb1a5f0818c5'
        result = self.app.get(endpoint, status=401)
        self.assertEqual(result.status, 401)

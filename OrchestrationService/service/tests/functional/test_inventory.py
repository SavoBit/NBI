import json

from service.tests.functional import InventoryTestCase


class TestInveontory(InventoryTestCase):
    ROUTE = '/nbi/orchestration/api/services'

    def test_collect_services_unauth(self):
        """
        Test that validates an unauthenticated user can't access SELFNET services
        It asserts response code 401
        :return:
        """
        result = self.app.get(TestInveontory.ROUTE, headers={'X-Auth-Token': ""}, status=401)
        self.assertTrue(result.status, 401)

    def test_collect_services(self):
        """
        Test that validates getting the service list.
        It asserts the response code 200 and the service fields:
            created
            type
            id
            status
        :return:
        """
        result = self.app.get(TestInveontory.ROUTE, headers={'X-Auth-Token': self.cloud_admin})
        self.assertTrue(result.status, 200)
        data = json.loads(result.body.decode('utf-8'))
        for service in data:
            list(map(lambda field: self.assertTrue(field in service.keys()), ['created', 'type', 'id', 'status']))

    def test_collect_service(self):
        """
        Test that validates getting a specific service
        It asserts the response code 200
        :return:
        """
        result = self.app.get(TestInveontory.ROUTE + '/FW-001', headers={'X-Auth-Token': self.cloud_admin})
        self.assertTrue(result.status, 200)

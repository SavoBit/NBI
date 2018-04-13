import json

from pkg_resources import resource_filename as rf

from service.resources.app_package import PackageAPI
from service.tests.functional import AppcatalogueTestCase


class TestNBIAppCatalogue(AppcatalogueTestCase):
    ROUTE = '/nbi/catalogue/api/packages/'

    def test_get_all_apps(self):
        """
        Test that validates getting all apps.
        It asserts the response code 200
        :return:
        """
        result = self.app.get(TestNBIAppCatalogue.ROUTE, headers={'X-Auth-Token': self.cloud_admin})
        self.assertEqual(result.status, 200)

    def test_filter_app_class(self):
        """
        Test that validates getting all apps by class type
        It asserts the response code 200 and the class
        :return:
        """
        for field in PackageAPI.APP_CLASS_TYPES:
            result = self.app.get(TestNBIAppCatalogue.ROUTE,
                                  params='app-class={}'.format(field),
                                  headers={'X-Auth-Token': self.cloud_admin})
            self.assertEqual(result.status, 200)
            data = json.loads(result.body.decode('utf-8'))
            for app in data.get('app'):
                self.assertTrue(app.get('class') == field)

    def test_invalid_app_class(self):
        """
        Test that validates getting an invalid class type
        It asserts the response code 404
        :return:
        """
        result = self.app.get(TestNBIAppCatalogue.ROUTE, status=404,
                              params='app-class={}'.format('VNFM'),
                              headers={'X-Auth-Token': self.cloud_admin})
        self.assertEqual(result.status, 404)

    def test_get_part_app(self):
        """
        Test that validates getting an app part
        It asserts the response code 200 for each valid endpoint
        :return:
        """
        for field in PackageAPI.PACKAGE_ENDPOINTS:
            result = self.app.get(
                '{}{}/{}'.format(TestNBIAppCatalogue.ROUTE, '3f894e43-b213-4566-8138-94501139753b', field),
                headers={'X-Auth-Token': self.cloud_admin})

            self.assertEqual(result.status, 200)

    def test_get_invalid_part_app(self):
        """
        Test that validates getting an invalid app part
        It asserts the response code 404
        :return:
        """
        result = self.app.get(
            '{}{}/{}'.format(TestNBIAppCatalogue.ROUTE, '3f894e43-b213-4566-8138-94501139753b', 'app-test'), status=404,
            headers={'X-Auth-Token': self.cloud_admin})

        self.assertEqual(result.status, 404)

    def test_delete_invalid_app(self):
        """
        Test that validates deleting an invalid app
        It asserts the response code 400
        :return:
        """
        endpoint = TestNBIAppCatalogue.ROUTE + '111111'
        result = self.app.delete(endpoint, headers={'X-Auth-Token': self.cloud_admin}, status=400)
        self.assertEqual(result.status, 400)

    def test_complete_app_cicle(self):
        """
        Test that validates the full cicle of an app
        1 - Create the app, asserts the response code 201 and the id
        2 - Update the app, asserts the response code 200
        3 - Disable the app, asserts the response code 200
        4 - Delete the app, asserts the response code 204
        :return:
        """
        app_id = self.create_app()
        self.get_specific_app(app_id)
        self.update_app(app_id)
        self.disable_app(app_id)
        self.delete_app(app_id)

    def create_app(self):
        result = self.app.post(TestNBIAppCatalogue.ROUTE,
                               headers={'X-Auth-Token': self.cloud_admin},
                               upload_files=[('file', rf(__name__, 'etc/vnf-test.tar'))])

        self.assertTrue(result.status)
        data = json.loads(result.body.decode('utf-8'))
        self.assertTrue('app' in data)
        self.assertTrue('id' in data.get('app'))
        return data.get('app').get('id')

    def get_specific_app(self, app_id):
        result = self.app.get(TestNBIAppCatalogue.ROUTE + app_id,
                              headers={'X-Auth-Token': self.cloud_admin})
        self.assertEqual(result.status, 200)

    def update_app(self, app_id):

        update_app = {
            "app": {
                "app-id": app_id,
                "metadata": {
                    "app-family": "SENSOR",
                    "app-class": "VNF",
                    "app-type": "test.type",
                    "app-name": "Test",
                    "app-version": "50.0",
                    "upload": False
                }
            }
        }

        result = self.app.put(TestNBIAppCatalogue.ROUTE + app_id, headers={'X-Auth-Token': self.cloud_admin},
                              params=json.dumps(update_app))
        self.assertTrue(result.status, 200)

    def disable_app(self, app_id):
        result = self.app.put(TestNBIAppCatalogue.ROUTE + app_id + '/disable',
                              headers={'X-Auth-Token': self.cloud_admin})
        self.assertTrue(result.status, 200)

    def delete_app(self, app_id):
        result = self.app.delete(TestNBIAppCatalogue.ROUTE + app_id,
                                 headers={'X-Auth-Token': self.cloud_admin})
        self.assertTrue(result.status, 204)

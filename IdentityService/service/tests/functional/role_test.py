import json

from service.tests.functional import KeystoneTestCase


class TestNBIRole(KeystoneTestCase):
    ROUTE = '/nbi/identity/api/roles/'

    CREATE_ROLE = json.dumps({
        "role": {
            "name": "test"
        }
    })

    def test_list_roles(self):
        """
        Test that an admin user can list all SELFNET roles.
        It asserts the response code 200 and the response body:
            roles: Object containing all roles
                id: the role id
                name: the role name
        :return:
        """
        result = self.app.get(TestNBIRole.ROUTE, headers={'X-Auth-Token': self.cloud_admin})
        self.assertEqual(result.status, 200)
        data = json.loads(result.body.decode('utf-8'))
        self.assertTrue('roles' in data)
        for field in ['name', 'id']:
            self.assertTrue(field in data.get('roles')[0])

    def test_create_roles(self):
        """
        Test that a cloud admin user can create SELFNET roles.
        It asserts the response code 201
        :return:
        """
        result = self.app.post(TestNBIRole.ROUTE, headers={'X-Auth-Token': self.cloud_admin},
                               params=TestNBIRole.CREATE_ROLE)
        self.assertEqual(result.status, 201)

    def test_invalid_user_list_roles(self):
        """
        Test that a regular user can't list SELFNET roles.
        It asserts the response code 403 and the response body:
            title: The title of the error identifying invalid credentials
            description: A brief description of the error
        :return:
        """
        result = self.app.get(TestNBIRole.ROUTE, status=403, headers={'X-Auth-Token': self.tenant_user})
        self.assertEqual(result.status, 403)
        data = json.loads(result.body.decode('utf-8'))
        for field in ['description', 'title']:
            self.assertTrue(field in data)

    def test_invalid_user_create_roles(self):
        """
        Test that a regular admin or user admin user can't create SELFNET roles.
        It asserts the response code 403
        :return:
        """
        result = self.app.post(TestNBIRole.ROUTE, status=403, headers={'X-Auth-Token': self.tenant_admin},
                               params=TestNBIRole.CREATE_ROLE)
        self.assertEqual(result.status, 403)

    def test_delete_role(self):
        """
        Test that a cloud admin user can delete SELFNET roles.
        It asserts the response code 204
        :return:
        """
        result = self.app.delete(TestNBIRole.ROUTE + '9fe2ff9ee4384b1894a90878d3e92bab',
                                 headers={'X-Auth-Token': self.cloud_admin})
        self.assertEqual(result.status, 204)

    def test_invalid_user_delete_role(self):
        """
        Test that a regular admin or user can't delete SELFNET roles.
        It asserts the response code 201
        :return:
        """
        result = self.app.delete(TestNBIRole.ROUTE + '9fe2ff9ee4384b1894a90878d3e92bab',
                                 headers={'X-Auth-Token': self.cloud_admin})

        self.assertEqual(result.status, 204)

import json
from copy import deepcopy

from service.tests.functional import KeystoneTestCase


class TestNBIUser(KeystoneTestCase):
    ROUTE = "/nbi/identity/api/tenants/a1cac2fb341c4ad5bcfb44cc43395209/users/"

    CREATE_USER = {
        "user": {
            "description": "New User",
            "username": "user_nbi_",
            "password": "user_nbi_",
            "role": {
                "id": "674fc98abdfb4e1daae5f95552c1bdc9"
            }
        }
    }

    UPDATE_USER = {
        "user": {
            "description": "This is a new message",
            "role": {
                "id": "7be94a48b0264adea47cd65036d90401"
            }
        }
    }

    def test_list_tenant_users(self):
        """
        Test that an admin user can list the users within its tenant
        It asserts the response code 200 and the response body:
            users:
                id: the user id
                username: user name to login
                description: user description
                links: the user url links
                role:
                    id: role unique identifier
                    name: role name
        :return:
        """

        result = self.app.get(TestNBIUser.ROUTE,
                              headers={'X-Auth-Token': self.tenant_admin})

        self.assertEqual(result.status, 200)
        data = json.loads(result.body.decode('utf-8'))
        self.assertTrue('users' in data)
        user = data.get('users')[0]
        for field in ['id', 'username', 'description', 'links', 'role']:
            self.assertTrue(field in user)

        for field in ['id', 'name']:
            self.assertTrue(field in user.get('role'))

    def test_list_invalid_tenant_user(self):
        """
        Test that a regular admin user can't list SELFNET users within its tenant.
        It asserts the response code 403
        :return:
        """
        result = self.app.get(TestNBIUser.ROUTE, status=403,
                              headers={'X-Auth-Token': self.tenant_user})

        self.assertEqual(result.status, 403)

    def test_create_user(self):
        """
        Test that an admin can create new users on its tenant.
        It validates the response code 201 and the presence of mandatory user fields
            user:
                username: user username to perform the login
                password: user password to perform the login
                role:
                    id: user role within the tenant
        and response fields
            user:
                id: the user id
                username: user name to login
                description: user description
                links: the user url links
                role:
                    id: role unique identifier
                    name: role name
        :return:
        """
        result = self.app.post(TestNBIUser.ROUTE, headers={'X-Auth-Token': self.cloud_admin},
                               params=json.dumps(TestNBIUser.CREATE_USER))

        self.assertEqual(result.status, 201)

        data = json.loads(result.body.decode('utf-8'))
        self.assertTrue('user' in data)
        user = data.get('user')
        for field in ['id', 'username', 'description', 'links', 'role']:
            self.assertTrue(field in user)

        for field in ['id']:
            self.assertTrue(field in user.get('role'))

    def test_create_invalid_user_object(self):
        """
        Validate an invalid body can't be successfully used to create a user.
        The test recursively removes one of the mandatory login fields.
        It asserts the response code 400 and the error format:
            title: The title of the error identifying invalid credentials
            description: A brief description of the error
            code: 002 meaning a format body error
        :return:
        """
        for field in ['username', 'password', 'role']:
            raw_message = deepcopy(TestNBIUser.CREATE_USER)
            raw_message['user'].pop(field)
            result = self.app.post(TestNBIUser.ROUTE, status=400, headers={'X-Auth-Token': self.tenant_admin},
                                   params=json.dumps(raw_message))
            data = json.loads(result.body.decode('utf-8'))
            self.assertEqual(result.status, 400)
            self.assertTrue('title' in data)
            self.assertTrue('description' in data)
            self.assertTrue('code' in data and data.get('code') == '002')
            self.assertTrue('request-id' in result.header_dict)

    def test_create_user_invalid_auth(self):
        """
        Test that a regular admin user can update SELFNET users within its tenant.
        It asserts the response code 403
        :return:
        """
        result = self.app.post(TestNBIUser.ROUTE + 'b0ac2a08f1eb406f9936a4cceb3ab7eb', status=403,
                               headers={'X-Auth-Token': self.tenant_user})
        self.assertEqual(result.status, 403)

    def test_update_user(self):
        """
        Test that a tenant admin user can update a given user.
        It asserts the response code 200 and the response body:
            user:
                id: the user id
                username: user name to login
                description: user description with new field
                links: the user url links
                role:
                    id: role unique identifier with the new role
                    name: role name
        :return:
        """
        result = self.app.patch(TestNBIUser.ROUTE + 'b0ac2a08f1eb406f9936a4cceb3ab7eb',
                                headers={'X-Auth-Token': self.tenant_admin}, params=json.dumps(TestNBIUser.UPDATE_USER))
        self.assertEqual(result.status, 200)

        data = json.loads(result.body.decode('utf-8'))
        self.assertTrue('user' in data)
        user = data.get('user')
        self.assertEqual(user.get('description'), TestNBIUser.UPDATE_USER.get('user').get('description'))
        self.assertEqual(user.get('role').get('id'), TestNBIUser.UPDATE_USER.get('user').get('role').get('id'))

    def test_update_user_invalid(self):
        """
        Test that a regular user can't update SELFNET users within its tenant.
        It asserts the response code 403
        :return:
        """
        result = self.app.patch(TestNBIUser.ROUTE + 'b0ac2a08f1eb406f9936a4cceb3ab7eb', status=403,
                                headers={'X-Auth-Token': self.tenant_user})
        self.assertEqual(result.status, 403)

    def test_delete_user(self):
        """
        Test that a tenant admin user can delete SELFNET users.
        It asserts the response code 204
        :return:
        """
        result = self.app.delete(TestNBIUser.ROUTE + 'b0ac2a08f1eb406f9936a4cceb3ab7eb',
                                 headers={'X-Auth-Token': self.tenant_admin})

        self.assertEqual(result.status, 204)

    def test_delete_invalid_user(self):
        """
        Test that a regular user can't delete SELFNET users.
        It asserts the response code 403
        :return:
        """
        result = self.app.delete(TestNBIUser.ROUTE + 'b0ac2a08f1eb406f9936a4cceb3ab7eb', status=403,
                                 headers={'X-Auth-Token': self.tenant_user})
        self.assertEqual(result.status, 403)

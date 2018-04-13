import json
from copy import deepcopy

from service.tests.functional import AuthTest


class TestNBIAuth(AuthTest):
    ROUTE = '/nbi/auth/api/login'

    VALID_LOGIN = {
        "auth": {
            "username": "admin",
            "password": "SELFNET@admin",
            "tenant": "default"
        }
    }

    INVALID_LOGIN = json.dumps({
        "auth": {
            "username": "__admin__",
            "password": "SELFNET@admin",
            "tenant": "default"
        }
    })

    def test_get_valid_auth(self):
        """
        Test that validates a valid login.
        It asserts the response code 201 and the response headers that must contain:
            request-id: Unique request identifier
            x-subject-token: Token that must be used in every request
        :return:
        """
        result = self.app.post(TestNBIAuth.ROUTE, params=json.dumps(TestNBIAuth.VALID_LOGIN))
        self.assertEqual(result.status, 201)
        self.assertTrue('request-id' in result.header_dict)
        self.assertTrue('x-subject-token' in result.header_dict)

    def test_invalid_auth(self):
        """
        Validates a user with invalid credentials can't login.
        It asserts the response code 401 and the absence of response headers and the error format:
            title: The title of the error identifying invalid credentials
            description: A brief description of the error
        :return:
        """
        result = self.app.post(TestNBIAuth.ROUTE, status=401, params=TestNBIAuth.INVALID_LOGIN)
        self.assertEqual(result.status, 401)
        data = json.loads(result.body.decode('utf-8'))
        self.assertTrue('title' in data)
        self.assertTrue('description' in data)
        self.assertTrue('request-id' in result.header_dict)
        self.assertTrue('x-subject-token' not in result.header_dict)

    def test_invalid_message(self):
        """
        Validate an invalid body can't be successfully logged in. The test recursively removes one of the mandatory
        login fields.
        It asserts the response code 400 and the absence of response headers and the error format:
            title: The title of the error identifying invalid credentials
            description: A brief description of the error
            code: 002 meaning a format body error
        :return:
        """
        for field in ['tenant', 'username', 'password']:
            raw_message = deepcopy(TestNBIAuth.VALID_LOGIN)
            raw_message['auth'].pop(field)
            result = self.app.post(TestNBIAuth.ROUTE, status=400, params=json.dumps(raw_message))
            data = json.loads(result.body.decode('utf-8'))
            self.assertEqual(result.status, 400)
            self.assertTrue('title' in data)
            self.assertTrue('description' in data)
            self.assertTrue('code' in data and data.get('code') == '002')
            self.assertTrue('request-id' in result.header_dict)
            self.assertTrue('x-subject-token' not in result.header_dict)

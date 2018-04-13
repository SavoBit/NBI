import unittest

import requests
from paste.deploy import loadapp
from paste.fixture import TestApp
from pkg_resources import resource_filename as rf


class TestNBIAPP(TestApp):
    def patch(self, url, params=b'', headers=None, extra_environ=None,
              status=None, upload_files=None, expect_errors=False):
        return self._gen_request('PATCH', url, params=params, headers=headers,
                                 extra_environ=extra_environ, status=status,
                                 upload_files=upload_files,
                                 expect_errors=expect_errors)


class MonitoringTestCase(unittest.TestCase):
    def setUp(self):
        self.app = TestNBIAPP(loadapp('config:' + rf(__name__, 'wsgi.ini')))

        # Login the necessary users
        self.cloud_admin = self.login_user()

    def login_user(self):
        auth = {
            "auth": {
                "identity": {
                    "methods": [
                        "password"
                    ],
                    "password": {
                        "user": {
                            "name": "admin",
                            "password": "SELFNET@admin",
                            "domain": {
                                "id": "default",
                                "name": "Default"
                            }
                        }
                    }
                },
                "scope": {
                    "domain": {
                        "id": "default",
                        "name": "Default"
                    }
                }
            }
        }
        r = requests.post('http://localhost:35357/v3/auth/tokens', json=auth)
        return r.headers.get('X-Subject-Token')

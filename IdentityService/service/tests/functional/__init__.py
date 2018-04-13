import json
import unittest
from subprocess import Popen, PIPE

from oslo_config import cfg
from oslo_policy import policy
from paste.deploy import loadapp
from paste.fixture import TestApp
from pkg_resources import resource_filename as rf

from service.__main__ import start_conf
from service.authz.policy import Policy


class TestNBIAPP(TestApp):
    def patch(self, url, params=b'', headers=None, extra_environ=None,
              status=None, upload_files=None, expect_errors=False):
        return self._gen_request('PATCH', url, params=params, headers=headers,
                                 extra_environ=extra_environ, status=status,
                                 upload_files=upload_files,
                                 expect_errors=expect_errors)


class TestCase(unittest.TestCase):
    def setUp(self):
        self.app = TestNBIAPP(loadapp('config:' + rf(__name__, 'wsgi.ini')))

    def __execute_command__(self, command):
        process = Popen(command, stdout=PIPE, stdin=PIPE, shell=True)
        process.communicate()


class AuthTest(TestCase):
    def setUp(self):
        super(AuthTest, self).setUp()
        #self.__execute_command__('echo "DROP DATABASE keystone;" | mysql -u root -proot -h 127.0.0.1')

    def tearDown(self):
        #self.__execute_command__('echo "CREATE DATABASE keystone;" | mysql -u root -proot -h 127.0.0.1')
        # Restore Dump
        self.__execute_command__('mysql keystone -h 127.0.01 -u root -proot < {}'.format(
            rf(__name__, 'etc/keystone_dump.sql')
        ))


class KeystoneTestCase(AuthTest):
    def setUp(self):
        super(KeystoneTestCase, self).setUp()

        # Login the necessary users
        self.cloud_admin = self.__login_user__('admin', 'SELFNET@admin', 'default')
        self.tenant_user = self.__login_user__('user_nbi', 'user_nbi', 'NBI_DOM_1')
        self.tenant_admin = self.__login_user__('admin_nbi', 'admin_nbi', 'NBI_DOM_1')

        # Start oslo_config
        start_conf(config_location=[rf(__name__, 'etc/oslo_conf.ini')])
        self.__init_enforcer__()

    def tearDown(self):
        super(KeystoneTestCase, self).tearDown()

    def __login_user__(self, username, password, tenant):
        auth = dict(username=username, password=password, tenant=tenant)
        result = self.app.post('/nbi/auth/api/login', params=json.dumps(dict(auth=auth)))
        return result.header_dict.get('x-subject-token')

    def __init_enforcer__(self):
        Policy.ENFORCER = policy.Enforcer(cfg.CONF, policy_file='policy.json')

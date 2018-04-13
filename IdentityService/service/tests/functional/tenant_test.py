import json
from copy import deepcopy

from service.tests.functional import KeystoneTestCase


class TestNBITenant(KeystoneTestCase):
    ROUTE = '/nbi/identity/api/tenants/'

    CREATE_TENANT = {
        "tenant": {
            "name": "NBI_DOM_2",
            "description": "The new test tenant",
            "enabled": True
        }
    }

    def test_list_tenants(self):
        """
        Test that a cloud admin user can list all SELFNET tenants.
        It asserts the response code 200 and the response body:
            tenants: Object containing all tenants
                id: the tenant id
                name: the tenant name
                description: the tenant description
                links: the tenant url links
                enabled: boolean checking if tenant is enabled or not
        :return:
        """
        result = self.app.get(TestNBITenant.ROUTE, headers={'X-Auth-Token': self.cloud_admin})
        self.assertEqual(result.status, 200)
        data = json.loads(result.body.decode('utf-8'))
        self.assertTrue('tenants' in data)
        tenant = data.get('tenants')[0]
        for field in ['description', 'enabled', 'links', 'name', 'id']:
            self.assertTrue(field in tenant)

    def test_list_sepcific_tenant(self):
        """
        Test that a cloud admin user can list a specific SELFNET tenants.
        It asserts the response code 200 and the response body:
            tenants: Object containing all tenants
                id: the tenant id
                name: the tenant name
                description: the tenant description
                links: the tenant url links
                enabled: boolean checking if tenant is enabled or not
        :return:
        """
        result = self.app.get(TestNBITenant.ROUTE + 'a1cac2fb341c4ad5bcfb44cc43395209',
                              headers={'X-Auth-Token': self.cloud_admin})
        self.assertEqual(result.status, 200)
        data = json.loads(result.body.decode('utf-8'))
        self.assertTrue('tenant' in data)
        tenant = data.get('tenant')
        for field in ['description', 'enabled', 'links', 'name', 'id']:
            self.assertTrue(field in tenant)

    def test_invalid_user_list_tenant(self):
        """
        Test that an admin user can't list SELFNET tenants.
        It asserts the response code 403
        """
        result = self.app.get(TestNBITenant.ROUTE, status=403, headers={'X-Auth-Token': self.tenant_admin})
        self.assertEqual(result.status, 403)

    def test_create_tenant(self):
        """
        Test that a cloud admin can create new tenants.
        It validates the response code 201 and the presence of mandatory tenant fields
            tenant:
                name: the name of the tenant to be created
        and response fields
            id: the tenant id
                name: the tenant name
                description: the tenant description
                links: the tenant url links
                enabled: boolean checking if tenant is enabled or not
        :return:
        """
        result = self.app.post(TestNBITenant.ROUTE, headers={'X-Auth-Token': self.cloud_admin},
                               params=json.dumps(TestNBITenant.CREATE_TENANT))
        self.assertEqual(result.status, 201)
        data = json.loads(result.body.decode('utf-8'))
        self.assertTrue('tenant' in data)
        tenant = data.get('tenant')
        for field in ['description', 'enabled', 'links', 'name', 'id']:
            self.assertTrue(field in tenant)

    def test_create_invalid_tenant(self):
        """
        Test that a cloud admin needs to provide a valid tenant object with the required fields.
        It validates the response code 400 and the presence of mandatory tenant fields
            tenant:
                name: the name of the tenant to be created
        :return:
        """
        raw_message = deepcopy(TestNBITenant.CREATE_TENANT)
        raw_message['tenant'].pop('name')
        result = self.app.post(TestNBITenant.ROUTE, status=400, headers={'X-Auth-Token': self.cloud_admin},
                               params=json.dumps(raw_message))
        self.assertEqual(result.status, 400)

    def test_invalid_user_create_tenant(self):
        """
        Test that an admin user can't create SELFNET tenants.
        It asserts the response code 403
        """
        result = self.app.post(TestNBITenant.ROUTE, status=403, headers={'X-Auth-Token': self.tenant_admin})
        self.assertEqual(result.status, 403)

    def test_update_tenant(self):
        """
        Test that a cloud admin can update a SELFNET tenant
        it asserts the response code 200 and the object response
        :return:
        """
        raw_message = deepcopy(TestNBITenant.CREATE_TENANT)

        msg = 'This was a tenant change'

        raw_message['tenant']['description'] = msg
        result = self.app.patch(TestNBITenant.ROUTE + 'a1cac2fb341c4ad5bcfb44cc43395209', status=200,
                                headers={'X-Auth-Token': self.cloud_admin},
                                params=json.dumps(raw_message))
        self.assertTrue(result.status, 200)
        data = json.loads(result.body.decode('utf-8'))
        self.assertTrue('tenant' in data)
        tenant = data.get('tenant')
        self.assertTrue('description' in tenant)
        self.assertEqual(tenant.get('description'), msg)

        result = self.app.get(TestNBITenant.ROUTE + 'a1cac2fb341c4ad5bcfb44cc43395209', status=200,
                              headers={'X-Auth-Token': self.cloud_admin})

        data = json.loads(result.body.decode('utf-8'))
        self.assertTrue('tenant' in data)
        tenant = data.get('tenant')
        self.assertEqual(tenant.get('description'), msg)

    def test_invalid_user_update_tenant(self):
        """
        Test that an admin user can't update SELFNET tenants.
        It asserts the response code 403
        """
        result = self.app.post(TestNBITenant.ROUTE, status=403, headers={'X-Auth-Token': self.tenant_admin})
        self.assertEqual(result.status, 403)

    def test_delete_tenant(self):
        """
        It validates a cloud admin user can delete a given SELFNET tenant
        it asserts the response code 204
        :return:
        """
        result = self.app.delete(TestNBITenant.ROUTE + 'a1cac2fb341c4ad5bcfb44cc43395209',
                                 headers={'X-Auth-Token': self.cloud_admin})
        self.assertEqual(result.status, 204)

    def test_invalid_user_delete_tenant(self):
        """
        Test that an admin user can't delete SELFNET tenants.
        It asserts the response code 403
        :return:
        """
        result = self.app.post(TestNBITenant.ROUTE, status=403, headers={'X-Auth-Token': self.tenant_admin})
        self.assertEqual(result.status, 403)

import json

from falcon import before, HTTP_200, HTTP_201, HTTP_204, HTTPNotFound

from service.resources import BaseResource, validate
from service.schema import load_schema
from service.requester import request, request_post_patch

from service.authz.policy import enforce
from service.conf_reader import ConfReader


def validate_id(req, resp, tenant_id):
    """
    Validate if the id is on the endpoint
    """
    if not tenant_id:
        raise HTTPNotFound()


class TenantAPI(BaseResource):
    """
    API that allows tenant management. This API exposes an Option, GET, POST, PATCH and DELETE Methods. This converts
    Keystone Domain objects into simple Tenant objects. All methods translate keystone URI to internal URI.
    """

    KS_ENDPOINT = ConfReader().get('keystone', 'url') + '/domains'

    ROUTES = [
        'tenants/',
        'tenants',
        'tenants/{tenant_id}',
        'tenants/{tenant_id}/'
    ]

    SERVICE_NAME = 'Tenant'

    @staticmethod
    def convert_domain_tenant(req, specific=True, r=None, domain=None):
        """
        Converts a Keystone Object in a tenant object. Corrects the links and removes the domain keyword.
        :param req: The request object to set the result
        :param specific: The original search was performed for a specific tenant
        :param r: The original request object to keystone with the response. If provided the data is
        loaded from the object.
        :param domain: The domain to convert. If provided the data is the object itself.
        :return: The tenant object
        """
        if r:
            data = json.loads(r.text)
            tenant = data['domain']
        else:
            tenant = domain

        tenant['links']['self'] = req.uri if specific else req.uri + '/' + tenant['id']
        return tenant

    def on_options(self, req, resp, **kargs):
        """
        OPTIONS method for the Tenant API
        :return:
        204 No Content - Header with the allow and all HTTP methods available
        """
        if kargs:
            resp.set_header('Allow', 'DELETE, GET, OPTIONS, PATCH')
        else:
            resp.set_header('Allow', 'GET, OPTIONS, POST')
        resp.status = HTTP_204

    @enforce(SERVICE_NAME, 'default')
    def on_get(self, req, resp, **kwargs):
        """
        List tenants. This method processes the HTTP get request for this API.
        If the tenant_id is provided the specific get tenant method is called,
        otherwise the get all tenants method is retrieved.
        """
        if kwargs:
            self.get_specific_tenant(req, resp, kwargs.get('tenant_id', None))
        else:
            self.get_all_tenants(req, resp)

    def get_all_tenants(self, req, resp):
        """
        Method to retrieve all tenants from the identity service. This endpoint is only accessible to Super ADMIN users.
        :return:
                200 OK - When all tenants are retrieved with success
        """
        r = request(
            TenantAPI.KS_ENDPOINT,
            headers={'X-Auth-Token': req.headers['X-AUTH-TOKEN']},
            service_name=TenantAPI.SERVICE_NAME
        )
        data = json.loads(r.text)

        # Convert object
        tenants = data.get('domains', None)
        tenants = list(map(lambda domain: self.convert_domain_tenant(req, specific=False, domain=domain), tenants))
        links = data.get('links', None)
        links["self"] = req.uri

        resp.body = self.format_body(dict(tenants=tenants, links=links), from_dict=True)

    def get_specific_tenant(self, req, resp, tenant_id):
        """
        Method to retrieve a single tenant. This endpoint is accessible to a Tenant Admin,
        that can only query it's tenant and Super Admin.
        :param tenant_id: Tenant ID to retrieve
        :return:
                200 OK - When the tenant is found and successfully retrieved
        """
        # Configure correct endpoint
        endpoint = TenantAPI.KS_ENDPOINT + '/' + tenant_id

        # Request the tenant
        r = request(
            endpoint,
            headers={'X-Auth-Token': req.headers['X-AUTH-TOKEN']},
            service_name=TenantAPI.SERVICE_NAME
        )
        tenant = TenantAPI.convert_domain_tenant(req, r=r)
        resp.body = self.format_body(dict(tenant=tenant), from_dict=True)
        resp.status = HTTP_200

    @enforce(SERVICE_NAME, 'default')
    @validate(load_schema('tenant'))
    def on_post(self, req, resp, parsed):
        """
        Method to create new tenant. This endpoint is accessible to Super Admin only.
        The name of each tenant must be unique.
        :return:
                201 Created - When the tenant is successfully created
        """
        data = parsed.get('tenant')

        # Build KS Request
        enabled = True  # By default a domain is enabled
        ks_domain = dict(name=data.get('name'), enabled=enabled, description=data.get('description'))

        # Process request
        r = request_post_patch(
            TenantAPI.KS_ENDPOINT, method='POST',
            headers={'Content-Type': 'application/json', 'X-Auth-Token': req.headers['X-AUTH-TOKEN']},
            json=dict(domain=ks_domain),
            service_name=TenantAPI.SERVICE_NAME
        )

        tenant = TenantAPI.convert_domain_tenant(req, r=r)
        resp.body = self.format_body(dict(tenant=tenant), from_dict=True)
        resp.status = HTTP_201

    @validate(load_schema('tenant_update'))
    @enforce(SERVICE_NAME, 'default')
    def on_patch(self, req, resp, tenant_id, parsed):
        """
        Method to update a Tenant. This endpoint is only accessible to the Super Admin.
        It's not required the full object only the updated fields.
        :param tenant_id: The tenant id to edit
        :return:
                200 OK - When the tenant is edited successfully
        """
        # Configure correct endpoint
        endpoint = TenantAPI.KS_ENDPOINT + '/' + tenant_id

        data = parsed.get('tenant')

        r = request_post_patch(
            endpoint, method='PATCH',
            headers={'Content-Type': 'application/json', 'X-Auth-Token': req.headers['X-AUTH-TOKEN']},
            json=dict(domain=data),
            service_name=TenantAPI.SERVICE_NAME
        )

        tenant = TenantAPI.convert_domain_tenant(req, r=r)
        resp.body = self.format_body(dict(tenant=tenant), from_dict=True)
        resp.status = HTTP_200

    @before(validate_id)
    @enforce(SERVICE_NAME, 'default')
    def on_delete(self, req, resp, tenant_id):
        """
        Method to delete a Tenant. This endpoint is only accessible to the Super Admin.
        Before deleting the tenant the method ensures the tenant is disabled.
        :param tenant_id: The tenant id to delete
        :return:
                204 No Content - When the tenant is successfully deleted
        """
        # Configure correct endpoint
        endpoint = TenantAPI.KS_ENDPOINT + '/' + tenant_id

        # Ensure the tenant is disabled
        ks_domain = dict(enabled=False)
        request_post_patch(
            endpoint, 'PATCH',
            headers={'Content-Type': 'application/json', 'X-Auth-Token': req.headers['X-AUTH-TOKEN']},
            json=dict(domain=ks_domain),
            service_name=TenantAPI.SERVICE_NAME
        )
        request(
            endpoint, method='DELETE',
            headers={'Content-Type': 'application/json', 'X-Auth-Token': req.headers['X-AUTH-TOKEN']},
            service_name=TenantAPI.SERVICE_NAME
        )
        resp.status = HTTP_204

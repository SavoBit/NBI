import json

from falcon import HTTP_200, HTTP_204, HTTP_201

from service.resources import BaseResource, validate
from service.requester import request, request_post_patch
from service.conf_reader import ConfReader
from service.schema import load_schema
from service.authz.policy import enforce


class RoleAPI(BaseResource):
    """
    API that allows querying the identity services for role ids and names.
    """

    KS_ENDPOINT = ConfReader().get('keystone', 'url') + '/roles'

    ROUTES = [
        'roles/',
        'roles',
        'roles/{role_id}',
        'roles/{role_id}/'
    ]

    SERVICE_NAME = 'Role'

    @staticmethod
    def convert_ks_role_role(role):
        """
        Converts a keystone role object in a simple role object
        :param role: The role to convert
        :return: Simple role object
        """
        role.pop('links', None)
        role.pop('domain_id', None)
        return role

    def on_options(self, req, resp):
        """
        OPTIONS method for the Role API
        :return:
        204 No Content - Header with the allow and all HTTP methods available
        """
        resp.set_header('Allow', 'GET, OPTIONS')
        resp.status = HTTP_204

    @enforce(SERVICE_NAME, 'list')
    def on_get(self, req, resp, **kwargs):
        """
        List roles. This method processes the HTTP get request for this API.
        If the role_id is provided the specific get role method is called,
        otherwise the get all roles method is retrieved.
        """
        if kwargs:
            self.get_specific_role(req, resp, kwargs.get('role_id'))
        else:
            self.get_all_roles(req, resp)

    def get_all_roles(self, req, resp):
        """
        Method to retrieve all roles from the identity service. This endpoint is only accessible to Super ADMIN users
        or tenant admin users. Only cross domain roles are shown, since there's no intention in creating special roles
        for each tenant.
        :return:
        200 OK - When all roles are retrieved with success
        Role Process Errors
        """
        r = request(
            RoleAPI.KS_ENDPOINT,
            headers={'X-Auth-Token': req.headers['X-AUTH-TOKEN']},
            service_name=RoleAPI.SERVICE_NAME
        )

        data = json.loads(r.text)
        data = data['roles']
        # Filter cross domain roles only
        data = list(filter(lambda role: not role.get('domain_id'), data))
        # Convert objects
        data = list(map(lambda role: RoleAPI.convert_ks_role_role(role), data))
        resp.body = self.format_body(dict(roles=data), from_dict=True)
        resp.status = HTTP_200

    def get_specific_role(self, req, resp, role_id):
        """
        Method to retrieve a single role based on its id
        :param role_id: The role id to search for.
        :return:
        200 OK - When all roles are retrieved with success
        404 Not Found - When the provided id don't exist on the identity service
        Role Process Errors
        """
        endpoint = RoleAPI.KS_ENDPOINT + '/' + role_id
        r = request(
            endpoint,
            headers={'X-Auth-Token': req.headers['X-AUTH-TOKEN']},
            service_name=RoleAPI.SERVICE_NAME
        )

        data = json.loads(r.text)
        role = data.get('role')
        role = RoleAPI.convert_ks_role_role(role)

        resp.body = self.format_body(dict(role=role), from_dict=True)
        resp.status = HTTP_200

    @validate(load_schema('role_create'))
    @enforce(SERVICE_NAME, "default")
    def on_post(self, req, resp, parsed):
        """
        Creates a Role object in a global context, i.e., accessible to all tenants
        :return:
                201 CREATED: Role created with success
        """
        data = parsed.get('role')
        request_post_patch(
            RoleAPI.KS_ENDPOINT, method='POST',
            headers={'X-Auth-Token': req.headers['X-AUTH-TOKEN']},
            json=dict(role=data)
        )

        resp.status = HTTP_201

    @enforce(SERVICE_NAME, "default")
    def on_delete(self, req, resp, role_id):
        """
        Deletes a given role
        :param role_id: The role id to be deleted
        :return:
            204 NO CONTENT: Role deleted with success
        """

        endpoint = RoleAPI.KS_ENDPOINT + '/' + role_id

        request(endpoint, method='DELETE', headers={'X-Auth-Token': req.headers['X-AUTH-TOKEN']})

        resp.status = HTTP_204

import json

from falcon import HTTP_200, HTTP_201, HTTP_204

from service.authz.policy import enforce
from service.conf_reader import ConfReader
from service.requester import request, request_post_patch
from service.resources import BaseResource, validate
from service.resources.role import RoleAPI
from service.resources.tenant import TenantAPI
from service.schema import load_schema

ADMIN_DOMAIN_ID = ConfReader().get('keystone', 'admin_tenant')
ADMIN_ROLE_NAME = 'admin'


class UserAPI(BaseResource):
    """
    API that allows user management. This API exposes an Option, GET, POST, PATCH and DELETE methods. This converts
    Keystone user objects into simple user objects. All methods translate keystone URI to internal URI.
    """

    KS_ENDPOINT = ConfReader().get('keystone', 'url') + '/users'
    SERVICE_NAME = 'User'

    ROUTES = [
        'tenants/{tenant_id}/users',
        'tenants/{tenant_id}/users/{user_id}',
    ]

    @staticmethod
    def __get_user_role__(req, tenant_id, user):
        """
        Internal method to query the identity service for the role of a specific user.
        This method converts the array roles into a single role object,
        since the user will only have a single role.
        :param req: WSGI request object to get the headers
        :param tenant_id: The tenant id to check user's role
        :param user: user object to request the role
        :return: User object with role key updated.
        """
        endpoint = "{}/{}/users/{}/roles/".format(
            TenantAPI.KS_ENDPOINT, tenant_id,
            user
        )

        r = request(
            endpoint,
            headers={'X-Auth-Token': req.headers['X-AUTH-TOKEN']},
            ignore_exception=True,
            service_name=UserAPI.SERVICE_NAME
        )

        if r.status_code != 200:
            return None  # If user requires himself without being admin can't see it's roles

        data = json.loads(r.text)
        data = data['roles']
        if data:
            # The user will only have a role in a tenant
            return dict(id=data[0]['id'], name=data[0]['name'])

    @staticmethod
    def convert_ks_user_user(req, specific=True, r=None, user=None):
        """
        Converts a Keystone Object in a user object. Corrects the links and removes the unnecessary keys.
        :param req: The request object to set the result
        :param r: The original request object to keystone with the response. If provided the data is
        loaded from the object.
        :param user: The user to convert. If provided the data is the object itself.
        :return: The user object
        """
        if r:
            data = json.loads(r.text)
            user = data['user']
        else:
            user = user

        role = UserAPI.__get_user_role__(req, user.get('domain_id'), user.get('id'))
        if role:
            user['role'] = role

        user['links']['self'] = req.uri if specific else req.uri + '/' + user['id']
        user.pop('domain_id', None)  # This field isn't be available in SELFNET
        user.pop('extra', None)  # This field isn't be available in SELFNET
        user.pop('password_expires_at', None)  # This field isn't be available in SELFNET
        user['username'] = user.pop('name', None)

        return user

    def on_options(self, req, resp, **kwargs):
        """
        OPTIONS method for the User API
        :return:
                204 No Content - Header with the allow and all HTTP methods available
        """
        if 'user_id' in kwargs:
            resp.set_header('Allow', 'DELETE, GET, OPTIONS, PATCH')
        else:
            resp.set_header('Allow', 'GET, OPTIONS, POST')
        resp.status = HTTP_204

    def on_get(self, req, resp, **kwargs):
        """
        List users. This method processes the HTTP get request for this API.
        If the user_id is provided the specific get user method is called,
        otherwise the get all users method is retrieved.
        The endpoint only acts upon a single tenant.
        """
        if 'user_id' in kwargs:
            self.get_specific_user(req, resp, kwargs.get('tenant_id', None), kwargs.get('user_id', None))
        else:
            self.get_all_tenant_users(req, resp, kwargs.get('tenant_id', None))

    def get_all_tenant_users(self, req, resp, tenant_id):
        """
        Method to retrieve all users from the identity service. This endpoint is only accessible to Super ADMIN users
        or tenant admin users.
        :param tenant_id: The tenant the users belong to
        :return:
                200 OK - When all users within a tenant are retrieved with success
        """
        r = request(
            UserAPI.KS_ENDPOINT,
            headers={'X-Auth-Token': req.headers['X-AUTH-TOKEN']},
            params=dict(domain_id=tenant_id),
            service_name=UserAPI.SERVICE_NAME
        )

        data = json.loads(r.text)
        users = data['users']
        # Converts keystone user and update the role
        users = list(map(lambda user: UserAPI.convert_ks_user_user(req, specific=False, user=user), users))
        #users = list(map(lambda user: UserAPI.__get_user_role__(req, tenant_id, user), users))

        resp.body = self.format_body(dict(users=users), from_dict=True)
        resp.status = HTTP_200

    def get_specific_user(self, req, resp, tenant_id, user_id):
        """
        Method to retrieve a single user. This endpoint is accessible to a Super ADMIN and Tenant Admin.
        :param tenant_id: The tenant the user belong to
        :param user_id: The user id to retrieve
        :return:
                200 OK - When the user is found and successfully retrieved
        """
        endpoint = UserAPI.KS_ENDPOINT + '/' + user_id

        # Request the User
        r = request(endpoint, headers={'X-Auth-Token': req.headers['X-AUTH-TOKEN']}, service_name=UserAPI.SERVICE_NAME)

        # Converts keystone user and update the role
        user = UserAPI.convert_ks_user_user(req, r=r)

        resp.body = self.format_body(dict(user=user))
        resp.status = HTTP_200

    @enforce(SERVICE_NAME, "create")
    @validate(load_schema('user_create'))
    def on_post(self, req, resp, tenant_id, parsed):
        """
        Method to create new user. This endpoint is accessible to Super Admin and tenant admin.
        The name of each user must be unique within a tenant.
        :return:
                201 Created - When the user is successfully created
        """
        data = parsed.get('user')

        # Validate Role ID
        role_endpoint = RoleAPI.KS_ENDPOINT + '/' + data.get('role').get('id')
        request(
            role_endpoint,
            headers={'Content-Type': 'application/json', 'X-Auth-Token': req.headers['X-AUTH-TOKEN']},
            service_name=UserAPI.SERVICE_NAME
        )

        # Build KS object
        ks_user = dict()
        ks_user['description'] = data.get('description', None)
        ks_user['name'] = data.get('username')
        ks_user['password'] = data.get('password')
        ks_user['enabled'] = data.get('enabled', True)
        ks_user['domain_id'] = tenant_id

        # Request user creation
        r = request_post_patch(
            UserAPI.KS_ENDPOINT, method='POST',
            headers={'Content-Type': 'application/json', 'X-Auth-Token': req.headers['X-AUTH-TOKEN']},
            json=dict(user=ks_user),
            service_name=UserAPI.SERVICE_NAME
        )

        # Get user object
        user = UserAPI.convert_ks_user_user(req, r=r)

        # Add specified role
        endpoint = "{}/{}/users/{}/roles/{}".format(
            TenantAPI.KS_ENDPOINT, tenant_id,
            user.get('id'), data.get('role').get('id')
        )

        request_post_patch(
            endpoint, method='PUT',
            headers={'X-Auth-Token': req.headers['X-AUTH-TOKEN']},
            service_name=UserAPI.SERVICE_NAME
        )

        user['role'] = dict(id=data.get('role').get('id'))
        resp.status = HTTP_201
        resp.body = self.format_body(dict(user=user))

    @enforce(SERVICE_NAME, "delete")
    def on_delete(self, req, resp, tenant_id, user_id):
        """
        Method to delete a user. This endpoint is only accessible to the Super Admin and tenant admin.
        The user is only deleted if disabled before.
        :param tenant_id: The tenant id where the user belongs to
        :return:
                204 No Content - When the tenant is successfully deleted
        """
        endpoint = UserAPI.KS_ENDPOINT + '/' + user_id

        request(
            endpoint, method='DELETE',
            headers={'X-Auth-Token': req.headers['X-AUTH-TOKEN']},
            service_name=UserAPI.SERVICE_NAME
        )
        resp.status = HTTP_204

    @enforce(SERVICE_NAME, 'update')
    @validate(load_schema('user_update'))
    def on_patch(self, req, resp, parsed, tenant_id, user_id):
        """
        Method to update a User. This endpoint is only accessible to the Super Admin and tenant admin.
        It's not required the full object only the updated fields.
        :return:
                200 OK - When the user is edited successfully
        """

        print('Im patching')
        # Validate incoming data
        data = parsed.get('user')

        # Build KS object based on user's role
        ks_user = dict()
        ks_user['description'] = data.get('description', None)
        ks_user['name'] = data.get('username', None)
        ks_user['enabled'] = data.get('enabled', None)

        ks_user['password'] = data.get('password', None)
        ks_user = {k: v for k, v in ks_user.items() if v is not None}  # Generator to clear None value keys

        # Patch or get user when only role is updated
        endpoint = UserAPI.KS_ENDPOINT + '/' + user_id

        r = request_post_patch(endpoint, method='PATCH', headers={'X-Auth-Token': req.headers['X-AUTH-TOKEN']},
                               json=dict(user=ks_user), service_name=UserAPI.SERVICE_NAME)

        # Converts keystone user and update the role
        user = UserAPI.convert_ks_user_user(req, r=r)

        if 'role' not in data:
            resp.status = HTTP_200
            resp.body = self.format_body(dict(user=user))
            return

        # Update role
        # Validate Role ID
        role_endpoint = RoleAPI.KS_ENDPOINT + '/' + data.get('role').get('id')
        request(
            role_endpoint,
            headers={'Content-Type': 'application/json', 'X-Auth-Token': req.headers['X-AUTH-TOKEN']},
            service_name=RoleAPI.SERVICE_NAME
        )

        # Disable current role
        role_id = user.get('role').get('id')

        endpoint = "{}/{}/users/{}/roles/{}".format(
            TenantAPI.KS_ENDPOINT, tenant_id,
            user_id, role_id
        )

        request(
            endpoint, method='DELETE',
            headers={'X-Auth-Token': req.headers['X-AUTH-TOKEN']},
            service_name=UserAPI.SERVICE_NAME
        )

        # Set new role
        endpoint = "{}/{}/users/{}/roles/{}".format(
            TenantAPI.KS_ENDPOINT, tenant_id,
            user_id, data.get('role').get('id')
        )
        request_post_patch(
            endpoint, method='PUT',
            headers={'X-Auth-Token': req.headers['X-AUTH-TOKEN']},
            service_name=RoleAPI.SERVICE_NAME
        )

        user['role'] = dict(id=data.get('role').get('id'))
        resp.status = HTTP_200
        resp.body = self.format_body(dict(user=user))

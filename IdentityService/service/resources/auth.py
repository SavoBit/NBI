import json
import logging

from falcon import HTTP_201, HTTP_204

from service.resources import BaseResource, validate
from service.schema import load_schema
from service.requester import request_post_patch
from service.conf_reader import ConfReader


class LoginAPI(BaseResource):
    """
    API to process the login request.
    """

    ROUTES = [
        'login/',
        'login',
    ]
    KS_ENDPOINT = ConfReader().get('keystone', 'url') + '/auth/tokens'
    SERVICE_NAME = 'AUTH'

    logger = logging.getLogger(__name__)

    def on_options(self, req, resp):
        """
        OPTIONS method for the Login API
        :return:
        204 No Content - An header with the allow and all HTTP methods available
        """
        resp.set_header('Allow', 'OPTIONS, POST')
        resp.status = HTTP_204

    @validate(load_schema('login'))
    def on_post(self, req, resp, parsed):
        """
        Create new token. This will issue a new request to the Keystone service that will launch a new token.
        :return:
        201 Created - When the new token is successfully created and the credentials are correct.
        An object with a JSON session representation is returned containing the issued_at, expires_at and user fields.
        """
        data = parsed.get('auth')

        # Build KS request
        ks_domain = dict(name=data.get('tenant'))  # In KS tenants are known as domains
        ks_user = dict(name=data.get('username'), password=data.get('password'), domain=ks_domain)
        ks_pw = dict(user=ks_user)

        ks_identity = dict(methods=['password'], password=ks_pw)
        ks_scope = dict(domain=ks_domain)
        ks_auth = dict(identity=ks_identity, scope=ks_scope)

        # Process request
        r = request_post_patch(
            LoginAPI.KS_ENDPOINT, method='POST',
            headers={'Content-Type': 'application/json'}, json=dict(auth=ks_auth)
        )

        resp.set_header('X-Subject-Token', r.headers['X-Subject-Token'])
        resp.status = HTTP_201

        data = json.loads(r.text)
        data = data['token']

        user = data['user']
        user['tenant'] = dict(id=user.get('domain').get('id'), name=user.get('domain').get('name'))

        user['role'] = data.pop('roles', None)[0]  # User's will only have one role
        user.pop('domain', None)
        data['user'] = user

        # Pop unwanted keys
        data.pop('catalog', None)
        data.pop('methods', None)
        data.pop('domain', None)

        self.format_body(dict(session=data), from_dict=True)
        LoginAPI.logger.info('User {} successfully logged'.format(user.get('id', None)))

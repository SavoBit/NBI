import json
from copy import deepcopy

import requests
from falcon.uri import parse_query_string

from service.conf_reader import ConfReader
from service.conf_reader import Singleton


def validate_token(func):
    """
    Decorator that forces the validation of the token
    :param func: FUnction to decorate
    """

    def func_wrapper(*args, **kwargs):
        Authenticate.validate_token()
        return func(*args, **kwargs)

    return func_wrapper


class Authenticate(metaclass=Singleton):
    """
    Class to manage the authentication process.
    It is a singleton so only one entity manages this process.
    """

    __TOKEN__ = None

    @staticmethod
    def get_token():
        return Authenticate.__TOKEN__

    @staticmethod
    def get_header():
        Authenticate.validate_token()
        return {'X-Auth-Token': Authenticate.__TOKEN__}

    @staticmethod
    def validate_token():
        Authenticate.__authenticate__(validate=True)

    @staticmethod
    def __authenticate__(validate=False):
        """
        Group of functions to authenticate the user on the MONASCA. This method can also validate the current token
        acquiring a new one if needed.
        :param validate: Validates the token and gets a new one if needed
        """

        def __get_auth_obj__():
            return json.loads(ConfReader().get('MONASCA_KEYSTONE', 'auth_obj', raw=True))

        def __build_path__():
            base_path = conf_obj.get('keystone')
            return base_path + 'auth/tokens' if base_path.endswith('/') else base_path + '/auth/tokens'

        def __auth__(auth_obj, path):
            resp = requests.post(path, json=auth_obj, headers={'Content-Type': 'application/json'},
                                 timeout=ConfReader().get('MONASCA', 'timeout'))

            if resp.status_code == 201:
                Authenticate.__TOKEN__ = resp.headers['X-Subject-Token']
            else:
                raise ValueError("Can't obtain master authentication to retrieve metrics: status code {} and message"
                                 "{}".format(resp.status_code, resp.json()))

        def __validate__(path):
            if not Authenticate.get_token():
                __auth__(__get_auth_obj__(), __build_path__())
            resp = requests.get(path, headers={'X-Auth-Token': Authenticate.get_token(),
                                               'X-Subject-Token': Authenticate.get_token()},
                                timeout=ConfReader().get('MONASCA', 'timeout'))

            if resp != 200:
                __auth__(__get_auth_obj__(), path)

        conf_obj = ConfReader().get_section_dict('MONASCA_KEYSTONE')
        if not validate:
            __auth__(__get_auth_obj__(), __build_path__())
        else:
            __validate__(__build_path__())


def paginate(func):
    """
    Decorator to force the pagination rewrite
    :param func:
    :return:
    """

    def func_wrapper(raw_obj, uri, req):
        if uri:
            links = deepcopy(raw_obj)
            pagination_links(links, uri, req)
            resource = func(raw_obj, uri, req)
            resource['links'] = links.get('links')
        else:
            resource = func(raw_obj, uri, req)
        return resource

    return func_wrapper


def pagination_links(raw_obj, uri, req):
    """
    Writes the pagination with the new URI
    :param raw_obj: The object containing the pagination objects
    :param uri: The URI string that originated the request
    """

    if 'links' not in raw_obj:
        return

    for link in raw_obj.get('links'):

        if link.get('rel') == 'next':
            qs = parse_query_string(link.get('href').rsplit('?')[-1])
            # Collect offset and limit
            offset = qs.get('offset', None)
            limit = qs.get('limit', None)

            # Collect base uri
            if '?' in uri:
                uri = req.uri.split('?')[0]
            else:
                uri = req.uri

            # Insert limit and offset for pagination
            uri = uri + '?'
            if offset:
                uri = uri + 'offset=' + offset + '&'
            if limit:
                uri = uri + 'limit=' + limit + '&'

            # Remove old limit and offset
            req.context.get('query_parameters').pop('offset', None)
            req.context.get('query_parameters').pop('limit', None)

            # Append remaining parameters
            query_string = '&'.join(
                ['{}={}'.format(key, value) for key, value in req.context.get('query_parameters').items()])

            uri = uri + query_string
            link['href'] = uri
            print(uri)

        elif link.get('rel') == 'self':
            link['href'] = req.uri

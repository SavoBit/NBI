import json
import logging

from falcon import HTTPBadRequest, HTTPNotFound, HTTP_200, HTTP_201, HTTP_204, before

from service.conf_reader import ConfReader
from service.requester import request_post_patch, request
from service.resources import BaseResource
from service.utils import parse_multiple_parameters

logger = logging.getLogger(__name__)

SERVIVE_NAME = 'APP Catalogue'


class PackageAPI(BaseResource):
    ROUTES = [
        "/packages",
        "/packages/",
        "/packages/{package_id}",
        "/packages/{package_id}/",
        "/packages/{package_id}/{endpoint}",
        "/packages/{package_id}/{endpoint}/"
    ]

    APP_CLASS_TYPES = ['VNF', 'SDN_APP', 'SDN_CTRL_APP', 'PNF']
    PACKAGE_ENDPOINTS = ["app-configuration", "app-descriptor", "app-monitoring", "app-info", "app-status"]

    # [Configuration, Descriptor, Monitor, Info, Status]
    PACKAGE_PUT_OPTIONS = ['enable', 'disable']

    def on_post(self, req, resp, **kwargs):
        """
        Creates a new package based on a provided file.
        """
        file = req.get_param('file')  # Loads the tar file
        if file is None:
            raise HTTPBadRequest(title="No Package", description="No package provided as file", code='215')

        endpoint = ConfReader().get('APP_CATALOGUE', 'url')
        r = request_post_patch(endpoint, method='POST', files={'file': file.file.read()})
        resp.status = HTTP_201
        resp.body = self.format_body(dict(app=dict(id=r.text)), from_dict=True)

    def on_delete(self, req, resp, **kwargs):
        if len(kwargs) != 1 or 'package_id' not in kwargs:
            raise HTTPNotFound()

        endpoint = '{}{}'.format(ConfReader().get('APP_CATALOGUE', 'url'), kwargs.get('package_id'))
        request(endpoint, method='DELETE')
        resp.status = HTTP_204

    def on_put(self, req, resp, **kwargs):

        # Load update object
        raw_json = req.stream.read()
        obj = json.loads(raw_json.decode('utf-8')) if raw_json else None

        if 'endpoint' in kwargs and kwargs.get('endpoint').lower() not in PackageAPI.PACKAGE_PUT_OPTIONS:
            raise HTTPNotFound()
        elif 'endpoint' in kwargs and kwargs.get('endpoint').lower() in PackageAPI.PACKAGE_PUT_OPTIONS:
            endpoint = '{}{}/{}'.format(ConfReader().get('APP_CATALOGUE', 'url'), kwargs.get('package_id'),
                                        'action')
            request_post_patch(endpoint, method='PUT', params=dict(status=kwargs.get('endpoint')))
        elif not obj or 'app' not in obj:
            raise HTTPBadRequest(title='No data', description='No data provided to update package', code='211')
        else:
            endpoint = "{}{}".format(ConfReader().get('APP_CATALOGUE', 'url'), kwargs.get('package_id'))
            request_post_patch(endpoint, method='PUT', json=obj.get('app'))

        resp.status = HTTP_200

    @before(parse_multiple_parameters)
    def on_get(self, req, resp, **kwargs):

        if 'endpoint' in kwargs:
            return self.__get_by_filter__(req, resp, kwargs.get('package_id', None), kwargs.get('endpoint'))

        # Get App based on the id
        # or
        # Get Apps based on the query string and app class or all
        self.__get_single_app__(req, resp, kwargs.get(
            'package_id')) if 'package_id' in kwargs else self.__get_all_packages__(req, resp)

    def __get_by_filter__(self, req, resp, package_id, endpoint):
        if endpoint.lower() not in PackageAPI.PACKAGE_ENDPOINTS:
            raise HTTPNotFound()

        __endpoint__ = "{}{}/{}".format(ConfReader().get('APP_CATALOGUE', 'url'), package_id, endpoint)
        r = request(__endpoint__)
        if r.text:
            resp.body = self.format_body({endpoint.lower()[len('app-'):]: json.loads(r.text)}, from_dict=True)
        else:
            resp.body = self.format_body({endpoint.lower()[len('app-'):]: {}}, from_dict=True)
        resp.status = HTTP_200

    def __get_single_app__(self, req, resp, package_id):
        endpoint = "{}/{}".format(ConfReader().get('APP_CATALOGUE', 'url'), package_id)
        r = request(endpoint)
        resp.body = self.format_body(dict(app=json.loads(r.text)), from_dict=True)

    def __get_all_packages__(self, req, resp):
        if 'app-class' in req.context.get('query_parameters', {}).keys() and req.context['query_parameters'].get(
                'app-class').upper() not in PackageAPI.APP_CLASS_TYPES:
            logger.info('User is requesting an invalid app type, {}'.format(req.context['query_parameters'].get(
                'app-class').upper()))
            raise HTTPNotFound()

        endpoint = ConfReader().get('APP_CATALOGUE', 'url') + 'ids'
        r = request(endpoint, params=req.context.get('query_parameters', {}))
        resp.body = self.format_body(dict(app=json.loads(r.text)), from_dict=True)

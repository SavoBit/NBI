import json
import re

import falcon
import jsonschema

import jsonpickle

__all__ = ['role', 'tenant', 'user', 'validate']


class BaseResource(object):

    @classmethod
    def initialize(cls):
        pass

    def format_body(self, data, from_dict=False, **kwargs):
        """
        Format the response body in JSON.
        :param data: The response body either in a class format or dict format
        :param from_dict: True if the data is in a dict format
        :param kwargs:
                        paginate: If the URI provides an offset that is manipulated by the NBI
        :return: Data in a JSON format
        """
        if from_dict:
            if 'paginate' in kwargs and 'req' in kwargs:
                BaseResource.__paginate__(data, kwargs.get('req'))
            return json.dumps(data)
        data = jsonpickle.encode(data, unpicklable=False)
        return data

    @staticmethod
    def __paginate__(data, req):
        """
        Paginates the response once the offset parameter is detected
        :param req: the request containing the URI
        :return: link object in the results dictionary
        """
        uri = req.uri

        links = list()
        links.append(dict(href=req.uri, rel='self'))
        if 'offset' in data:
            uri = re.sub('offset=.*?(&|$)', '', uri)
            index = uri.find('?')
            if index > 0 and len(req.query_context.keys()) > 0:
                uri = uri[:index + 1] + 'offset=' + str(req.query_context.get('offset')) + '&' + uri[index + 1:]
            elif index > 0:
                uri = uri[:index + 1] + 'offset=' + str(req.query_context.get('offset')) + uri[index + 1:]
            else:
                uri = uri[:index + 1] + '?offset=' + str(req.query_context.get('offset')) + uri[index + 1:]
            links.append(dict(href=uri, rel='next'))

        data['links'] = links


def validate(schema):
    """
    Validates a JSON schema and parse into an object to be used on an URL
    :param schema: the schema to be validated
    :return: parsed object into function signature
    """
    def decorator(func):
        def wrapper(self, req, resp, *args, **kwargs):
            try:
                raw_json = req.stream.read()
                obj = json.loads(raw_json.decode('utf-8'))
                obj['req_id'] = req.context.get('request_id')
            except Exception:
                raise falcon.HTTPBadRequest(
                    title='Invalid data',
                    description='Could not properly parse the provided data as JSON',
                    code='001'
                )

            try:
                jsonschema.validate(obj, schema)
            except jsonschema.ValidationError as e:
                raise falcon.HTTPBadRequest(
                    title='Failed data validation',
                    description=e.message,
                    code='002'
                )

            return func(self, req, resp, *args, parsed=obj, **kwargs)
        return wrapper
    return decorator

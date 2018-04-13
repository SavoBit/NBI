import json

import falcon
import jsonpickle
import jsonschema

__all__ = ['flow', 'flow_measurement', 'flow_metrics', 'vm_measurement', 'vm_metrics', 'alarm', 'alarm_definitions',
           'metric_measurements']


class BaseResource(object):

    @classmethod
    def initialize(cls):
        pass

    def format_body(self, data, from_dict=False):
        if from_dict:
            return json.dumps(data)
        data = jsonpickle.encode(data, unpicklable=False)
        return data


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'toJSON'):
            return obj.toJSON()
        else:
            return json.JSONEncoder.default(self, obj)


def validate(schema):
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

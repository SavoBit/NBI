from falcon import before

from service.conf_reader import ConfReader
from service.monasca_helper import Authenticate
from service.monasca_helper import paginate
from service.requester import request
from service.resources import BaseResource
from service.utils import parse_multiple_parameters


class Alarm(BaseResource):
    ENDPOINT = '/alarms'
    ROUTES = [
        '/alarms',
        '/alarms/',
        '/alarms/{alarm_id}',
        '/alarms/{alarm_id}/'
    ]

    @staticmethod
    @paginate
    def __convert_result__(raw_obj, uri, req):
        alarms = list([element for element in raw_obj.get('elements')]) if len(
            raw_obj.get('elements')) > 0 else []
        for alarm in alarms:
            alarm.pop('links')
            alarm.get('alarm_definition', {}).pop('links', {})
        return dict(alarms=alarms, links=raw_obj.get('links', {}))

    @before(parse_multiple_parameters)
    def on_get(self, req, resp, **kwargs):
        if 'alarm_id' in kwargs:
            self.get_single_alarm(req, resp, kwargs.get('alarm_id'))
        else:
            self.get_all_alarms(req, resp)

    def get_single_alarm(self, req, resp, alarm_id):
        headers = Authenticate.get_header()  # Insert the auth header
        r = request(ConfReader().get('MONASCA', 'url') + Alarm.ENDPOINT + '/' + alarm_id,
                    params=req.context['query_parameters'],
                    headers=headers)

        alarm = r.json()
        alarm.pop('links')
        alarm.pop('link')
        alarm.get('alarm_definition').pop('links')

        resp.body = self.format_body(alarm, from_dict=True)
        resp.status = str(r.status_code)

    def get_all_alarms(self, req, resp):
        if 'limit' not in req.context.get('query_parameters'):
            req.context.get('query_parameters')['limit'] = 5

        headers = Authenticate.get_header()  # Insert the auth header
        r = request(ConfReader().get('MONASCA', 'url') + Alarm.ENDPOINT, params=req.context['query_parameters'],
                    headers=headers)

        resp.body = self.format_body(Alarm.__convert_result__(r.json(), req.uri, req), from_dict=True)
        resp.status = str(r.status_code)

from service.conf_reader import ConfReader
from service.monasca_helper import Authenticate
from service.requester import request
from service.resources import BaseResource


class AlarmDefinition(BaseResource):
    ENDPOINT = '{}/alarm-definitions/{}'

    ROUTES = [
        '/alarm-definitions/{definition_id}',
        '/alarm-definitions/{definition_id}/',
    ]

    def on_get(self, req, resp, definition_id):
        headers = Authenticate.get_header()  # Insert the auth header
        r = request(AlarmDefinition.ENDPOINT.format(ConfReader().get('MONASCA', 'url'), definition_id), headers=headers)
        data = r.json()
        for field in ['links', 'alarm_actions', 'ok_actions', 'undetermined_actions']:
            data.pop(field, {})
        resp.body = self.format_body(dict(definition=data), from_dict=True)

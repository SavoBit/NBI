from falcon import before

from service.conf_reader import ConfReader
from service.monasca_helper import Authenticate, paginate
from service.requester import request
from service.resources import BaseResource
from service.utils import parse_multiple_parameters


class VMMetricsAPI(BaseResource):
    ENDPOINT = '/metrics/names'

    ROUTES = [
        '/vm/metrics/{instance_id}',
        '/vm/metrics/{instance_id}/'
    ]

    @staticmethod
    @paginate
    def __convert_result__(raw_obj, uri, req):
        """
        Converts the Monasca result in a SELFNET result
        :param raw_obj: Raw object provided by Monasca
        :param uri: String that originated the request
        :return: A dictionary with all VM metrics
        """
        metrics = list(map(lambda element: element['name'], raw_obj.get('elements'))) if len(
            raw_obj.get('elements')) > 0 else []
        return dict(metrics=metrics)

    @before(parse_multiple_parameters)
    def on_get(self, req, resp, instance_id):
        """
        Retrieve the list of metrics collected for a specific VM
        :param req: Request WSGI object
        :param resp: Response WSGI object
        :param instance_id: VM ID to search for the metrics.
        """
        dimensions_query = 'InstanceID:' + instance_id
        headers = Authenticate.get_header()  # Insert the auth header

        req.context['query_parameters']['dimensions'] = dimensions_query

        r = request(ConfReader().get('MONASCA', 'url') + VMMetricsAPI.ENDPOINT,
                    params=req.context['query_parameters'], headers=headers)

        req.context['query_parameters'].pop('dimensions')

        resp.body = self.format_body(VMMetricsAPI.__convert_result__(r.json(), req.uri, req), from_dict=True)
        resp.status = str(r.status_code)

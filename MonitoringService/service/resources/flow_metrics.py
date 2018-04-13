from falcon import before

from service.conf_reader import ConfReader
from service.monasca_helper import Authenticate, paginate
from service.requester import request
from service.resources import BaseResource
from service.utils import parse_multiple_parameters

SERVICE_NAME = 'Service Monitoring'


class FlowMetrics(BaseResource):
    ENDPOINT = '/metrics/names'

    ROUTES = [
        "/flow/metrics/{source}",
        "/flow/metrics/{source}/"
    ]

    @staticmethod
    @paginate
    def __convert_result__(raw_obj, uri, req):
        """
        Converts the Monasca result in a SELFNET result
        :param raw_obj: Raw object provided by Monasca
        :param uri: String that originated the request
        :return: A dictionary with all flows
        """
        metrics = list([element for element in raw_obj.get('elements')]) if len(
            raw_obj.get('elements')) > 0 else []

        return dict(metrics=metrics)

    @before(parse_multiple_parameters)
    def on_get(self, req, resp, source, **kwargs):
        """
        Retrieve the list of flow metrics collected on a given SourceIP. Additionally it can be provided the
        DestinationIP and DestinationPort. This method accepts also the start_time and end_time as query parameters
        :param source: SourceIP of the flow.
        :param kwargs: It can be: only DestinationIP or DestinationIP and DestinationPort
        :return: List with flow metrics
        """
        dimensions_query = 'FlowID:' + source
        if kwargs:
            dimensions_query += ',' + ','.join(['{}:{}'.format(key, value) for key, value in kwargs.items()])

        req.context['query_parameters']['dimensions'] = dimensions_query

        headers = Authenticate.get_header()  # Insert the auth header
        r = request(ConfReader().get('MONASCA', 'url') + FlowMetrics.ENDPOINT,
                    headers=headers,
                    params=req.context['query_parameters'])

        req.context['query_parameters'].pop('dimensions')

        resp.body = self.format_body(FlowMetrics.__convert_result__(r.json(), req.uri, req), from_dict=True)
        resp.status = str(r.status_code)

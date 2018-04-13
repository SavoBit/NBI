from datetime import datetime, timedelta

from falcon import HTTPNotFound, before, HTTPBadRequest

from service.conf_reader import ConfReader
from service.monasca_helper import Authenticate, paginate
from service.requester import request
from service.resources import BaseResource
from service.resources.flow_metrics import FlowMetrics
from service.utils import parse_multiple_parameters


class Flows(BaseResource):
    ENDPOINT = '/metrics/measurements'
    ROUTES = [
        '/flow/{source}/{DestinationIP}/{DestinationPort}',
        '/flow/{source}/{DestinationIP}/{DestinationPort}/',
        '/flow/{source}/{DestinationIP}',
        '/flow/{source}/{DestinationIP}/',
        '/flow/{source}',
        '/flow/{source}/'
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
        flows = list([element['dimensions'] for element in raw_obj.get('elements')]) if len(
            raw_obj.get('elements')) > 0 else []
        return dict(flows=flows)

    @staticmethod
    def __get_metric__(dimensions_query):
        """
        Collect all the metrics in a given flow.
        :param dimensions_query: Dictionary with all Source and Destination information.
        :return: List with metrics collected on a given flow
        """

        headers = Authenticate.get_header()  # Insert the auth header
        r = request(ConfReader().get('MONASCA', 'url') + FlowMetrics.ENDPOINT, params=dimensions_query, headers=headers)

        metrics = FlowMetrics.__convert_result__(r.json(), None, None).get('metrics')
        if len(metrics) == 0:
            raise HTTPNotFound
        return metrics

    @before(parse_multiple_parameters)
    def on_get(self, req, resp, source, **kwargs):
        """
        Retrieve the list of flows collected on a given SourceIP. Additionally it can be provided the
        DestinationIP and DestinationPort. This method accepts also the start_time and end_time as query parameters
        :param source: SourceIP of the flow.
        :param kwargs: It can be: only DestinationIP or DestinationIP and DestinationPort
        :return: List with flows
        """
        dimensions_query = 'SourceIP:' + source
        if kwargs:
            dimensions_query += ',' + ','.join(['{}:{}'.format(key, value) for key, value in kwargs.items()])

        req.context['query_parameters']['dimensions'] = dimensions_query

        if 'metric' not in req.context['query_parameters']:
            raise HTTPBadRequest(title='Missing Metric', description='Missing metric name to collect metrics',
                                 code='300')

        req.context['query_parameters']['name'] = req.context['query_parameters'].get('metric')
        req.context['query_parameters']['group_by'] = 'SourceIP,DestinationIP,DestinationPort,FlowID'
        req.context['query_parameters']['merge_metrics'] = 'true'

        if 'start_time' not in req.context['query_parameters']:
            d = datetime.now() - timedelta(days=1)
            req.context['query_parameters']['start_time'] = d.isoformat()

        headers = Authenticate.get_header()  # Insert the auth header
        r = request(ConfReader().get('MONASCA', 'url') + Flows.ENDPOINT, params=req.context['query_parameters'],
                    headers=headers)

        req.context['query_parameters'].pop('group_by')
        req.context['query_parameters'].pop('merge_metrics')
        req.context['query_parameters'].pop('name')

        resp.body = self.format_body(Flows.__convert_result__(r.json(), req.uri, req), from_dict=True)
        resp.status = str(r.status_code)

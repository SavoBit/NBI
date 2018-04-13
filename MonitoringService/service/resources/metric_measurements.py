from falcon import before

from service.conf_reader import ConfReader
from service.monasca_helper import Authenticate, paginate
from service.requester import request
from service.resources import BaseResource
from service.utils import parse_multiple_parameters


class MetricMeasurement(BaseResource):
    ENDPOINT = '/metrics/measurements'

    ROUTES = [
        "/metrics/{metric_name}/measurements/",
        "/metrics/{metric_name}/measurements"
    ]

    @staticmethod
    @paginate
    def __convert_result__(raw_obj, uri, req, measurements=True):
        """
        Converts the Monasca result in a SELFNET result
        :param raw_obj: Raw object provided by Monasca
        :param uri: String that originated the request
        :return: A dictionary with all measurements
        """
        if len(raw_obj.get('elements')) > 0:
            measurements = []
            for element in raw_obj.get('elements'):
                measurements += list(map(lambda m: dict(zip(element.get('columns'), m)), element.get('measurements')))
        else:
            measurements = []

        return dict(measurements=measurements)

    @before(parse_multiple_parameters)
    def on_get(self, req, resp, metric_name):
        req.context['query_parameters']['name'] = metric_name

        headers = Authenticate.get_header()  # Insert the auth header
        r = request(ConfReader().get('MONASCA', 'url') + MetricMeasurement.ENDPOINT,
                    headers=headers,
                    params=req.context['query_parameters'])

        resp.body = self.format_body(MetricMeasurement.__convert_result__(r.json(), req.uri, req), from_dict=True)
        resp.status = str(r.status_code)

from falcon import before

from service.resources.measurement import MeasurementAPI
from service.utils import parse_multiple_parameters


class FlowMeasurement(MeasurementAPI):
    ROUTES = [
        '/flow/measurements/{flow}/{metric}',
        '/flow/measurements/{flow}/{metric}/'
    ]

    @before(parse_multiple_parameters)
    def on_get(self, req, resp, flow, metric):
        """
        Retrieve the list of flow measurements on a given metric and flow. This method accepts also the
        start_time and end_time as query parameters
        :param flow: ID of the flow.
        :param metric: The metric name to search measurements
        :return: List with flow metric measurements
        """
        dimensions_query = 'FlowID:' + flow
        query_parameters = dict(dimensions=dimensions_query, name=metric)
        self.__query_measurements__(req, resp, query_parameters)

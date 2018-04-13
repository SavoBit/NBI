from service.conf_reader import ConfReader
from service.monasca_helper import Authenticate
from service.monasca_helper import paginate
from service.requester import request
from service.resources import BaseResource


class MeasurementAPI(BaseResource):
    ENDPOINT = '/metrics/measurements'

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

    def __query_measurements__(self, req, resp, query_parameters):
        """
        Method to construct the query string and retrieve the measurements from Monasca
        :param query_parameters: The InstanceID/FlowID and MetricID of the request
        """
        if 'query_parameters' in req.context:
            query_parameters.update(req.context['query_parameters'])

        headers = Authenticate.get_header()
        r = request(ConfReader().get('MONASCA', 'url') + MeasurementAPI.ENDPOINT, params=query_parameters,
                    headers=headers)
        resp.body = self.format_body(MeasurementAPI.__convert_result__(r.json(), req.uri, req), from_dict=True)
        resp.status = str(r.status_code)

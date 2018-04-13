from service.resources.measurement import MeasurementAPI


class VMMeasurementsAPI(MeasurementAPI):

    ROUTES = [
        '/vm/measurements/{instance_id}/{metric}',
        '/vm/measurements/{instance_id}/{metric}/'
    ]

    def on_get(self, req, resp, instance_id, metric):
        """
        Retrieve the list of metrics collected for a specific VM
        :param req: Request WSGI object
        :param resp: Response WSGI object
        :param instance_id: VM ID to search for the metrics.
        :param metric: The metric to search for.
        """
        dimensions_query = 'InstanceID:' + instance_id
        query_parameters = dict(dimensions=dimensions_query, name=metric)
        self.__query_measurements__(req, resp, query_parameters)

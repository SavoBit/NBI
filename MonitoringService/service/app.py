import inspect
import sys

import falcon
from falcon_cors import CORS

import service.utils as utils
from service.resources import *
from service.conf_reader import ConfReader
from service.middleware.context import ContextMiddleware
from service.middleware.log import LogMiddleware


class Service(falcon.API):
    def __init__(self):

        cors = CORS(allow_all_origins=True)

        super(Service, self).__init__(
            middleware=[cors.middleware, ContextMiddleware(), LogMiddleware()]
        )

        self.BASE_PATH = '/nbi/monitoring/api'

        # Build routes
        resources = __find_resources__()
        exclude_list = ConfReader().get_list('API', 'exclude_apis')
        if len(exclude_list) > 0:
            resources = list(
                filter(lambda api: api.__name__ not in exclude_list, resources)
            )
        for r in resources:
            r.initialize()
            instance = r()
            for route in r.ROUTES:
                self.add_route(self.BASE_PATH + route, instance)

    def start(self):
        """ A hook to when a Gunicorn worker calls run()."""
        pass

    def stop(self, signal):
        """ A hook to when a Gunicorn worker starts shutting down. """
        pass


def __find_resources__():
    resource_name = "{}.{}".format(utils.__find_route_module_name__(), "resources")

    # Find resource names
    resource_members = inspect.getmembers(sys.modules[resource_name], inspect.ismodule)
    resources = list(filter(lambda x: resource_name in str(x), resource_members))

    api_resources = list()
    for r in resources:
        classes = inspect.getmembers(sys.modules[r[1].__name__], inspect.isclass)
        api_resources.extend(classes)

    # Find resource classes
    api_resources = list(filter(lambda x: resource_name in str(x) and x[0] != 'BaseResource', api_resources))
    api_resources = list(map(lambda x: x[1], api_resources))
    return api_resources

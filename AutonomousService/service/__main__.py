from paste.urlmap import parse_path_expression, URLMap

from service.app import Service
from service.conf_reader import ConfReader
from service.gunicorn import GunicornApp
from service.logger.logging import setup_logging
from service.model.db.connector import connect_db


def urlmap_factory(loader, global_conf, **local_conf):
    """
    Hook for urlmap and gunicorn custom worker. Since the Gunicorn custom app forces the
    apps to have a start and stop method.
    """
    urlmap = URLMapGunicornHook(not_found_app=None)
    for path, app_name in local_conf.items():
        path = parse_path_expression(path)
        app = loader.get_app(app_name, global_conf=global_conf)
        urlmap[path] = app
    return urlmap


class URLMapGunicornHook(URLMap):
    """
    Gunicorn Hook for PasteDeploy with start and stop methods.
    """

    def start(self):
        """ A hook to when a Gunicorn worker calls run()."""
        pass

    def stop(self, signal):
        """ A hook to when a Gunicorn worker starts shutting down. """
        pass


#  *****Paste Factories*****

def app_factory(global_config, **local_config):
    return Service()


def server_factory(global_conf):
    """
    Gunicorn Server factory. It uses a custom gunicron app
    """

    def serve(app):
        gunicorn_app = GunicornApp(app, ConfReader().get_section_dict('GUNICORN'))

        # Load log configuration
        try:
            setup_logging(ConfReader().get('LOGGING', 'path'), ConfReader().get('LOGGING', 'level'))
        except PermissionError:
            print('Log not configured permission denied')

        connect_db(ConfReader().get_section_dict('INTELLIGENCE_DATABASE'))
        connect_db(ConfReader().get_section_dict('TAL_DATABASE'))

        gunicorn_app.run()

    return serve

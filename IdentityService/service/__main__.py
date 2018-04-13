from paste.urlmap import parse_path_expression, URLMap

from service.app import IdentityService, AuthService
from service.conf_reader import ConfReader
from service.gunicorn import GunicornApp
from service.logger.logging import setup_logging


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

def auth_factory(global_config, **local_config):
    return AuthService()


def app_factory(global_config, **local_config):
    return IdentityService()


def server_factory(global_conf):
    """
    Gunicorn Server factory. It uses a custom gunicron app
    """
    def serve(app):
        start_conf()  # Starts a oslo conf global variable required for oslo_policy
        gunicorn_app = GunicornApp(app, ConfReader().get_section_dict('GUNICORN'))

        # Load log configuration
        try:
            setup_logging(ConfReader().get('LOGGING', 'path'), ConfReader().get('LOGGING', 'level'))
        except PermissionError:
            print('Log not configured permission denied')
        gunicorn_app.run()

    return serve


def start_conf(config_location=None):
    """
    Since the oslo policy requires the usage of a global conf file this function
    starts the global conf variable.
    :note:
            Kesytone middleware configuration is repeated in oslo_config and wsgi.ini
            due to a strange behaviour.
    :return:
    """
    from oslo_config import cfg

    cfg.CONF(
        args=[],
        default_config_files=['service/etc/oslo_conf.ini'] if not config_location else config_location
    )

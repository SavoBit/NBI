from gunicorn.app.base import Application
from gunicorn.workers.sync import SyncWorker


class CustomWorker(SyncWorker):
    """
    Custom Syncworker to be used
    """
    def handle_quit(self, sig, frame):
        self.app.application.stop(sig)
        super().handle_quit(sig, frame)

    def run(self):
        self.app.application.start()
        super().run()


class GunicornApp(Application):
    """ Custom Gunicorn application
    This allows for us to load gunicorn settings from an external source
    """
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(GunicornApp, self).__init__()

    def load_config(self):

        # If available a profiling will be loaded to measure function times
        if 'profiling' in self.options.keys():
            __cfg__ = self.get_config_from_filename(self.options.pop('profiling'))

            for k, v in __cfg__.items():
                # Ignore unknown names
                if k not in self.cfg.settings:
                    continue
                self.cfg.set(k.lower(), v)

        # Load common gunicorn options
        for key, value in self.options.items():
            self.cfg.set(key.lower(), value)

        self.cfg.set('worker_class', 'service.gunicorn.CustomWorker')

    def load(self):
        return self.application

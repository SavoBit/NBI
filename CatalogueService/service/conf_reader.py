import configparser
import os
from ast import literal_eval as le

from pkg_resources import resource_filename as rf


class Singleton(type):
    """
    Creates a singleton instance for the parent class.
    This way only one instance will be available throughout the application.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ConfReader(metaclass=Singleton):
    """
    Read configuration from the ini file
    The class uses the ini_file input to read external or default file
    """

    def __init__(self, ini_file=None):
        self.config = configparser.ConfigParser(os.environ, allow_no_value=True)
        self.__internal__parser = configparser.ConfigParser(allow_no_value=True)
        if ini_file:
            self.config.read_file(open(ini_file))
            self.__internal__parser.read_file(open(ini_file))
        else:
            self.config.read(rf(__name__, 'etc/conf.ini'))
            self.__internal__parser.read(rf(__name__, 'etc/conf.ini'))

    def get(self, section, config, raw=False):
        return self.config.get(section, config) if raw else le(self.config.get(section, config))

    def get_list(self, section, config):
        return self.__internal__parser.get(section, config).split(',')

    def get_section_dict(self, section):
        configs_list = self.__internal__parser.items(section, raw=True) if section in self.config else None
        configs = dict()
        for key, value in configs_list:
            configs[key] = self.get(section, key)
        return configs

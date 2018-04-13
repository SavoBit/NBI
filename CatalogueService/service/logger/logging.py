import logging.config
import os

import pkg_resources
import yaml

import service.utils as utils


def findall(v, k, log_path):
    """
    Recursively find a key in a dictionary.
    This ignores arrays.
    :param v: Dict to search for the key
    :param k: Value to search for
    :param log_path: The path to add to the value
    """
    if isinstance(v, dict):
        for k1 in v:
            if k1 == k:
                v[k1] = os.path.join(log_path, v[k1])
            findall(v[k1], k, log_path)


def setup_logging(log_path, level=logging.INFO, log_file='logging.yaml'):
    """
    Setup logging by reading a yaml configuration file provided in the package.
    :param log_path: The directory where the logs must be stored
    :param level: The logging level to consider
    :param log_file: The file containing the configurations
    """

    # Load config file
    rp = __name__
    path = os.path.join('config', log_file)
    path = pkg_resources.resource_string(rp, path)
    config = yaml.load(path)

    # Create log path and Edit log file paths
    try:
        os.makedirs(log_path, exist_ok=True)
        findall(config, "filename", log_path)
    except PermissionError as e:
        import sys
        print("Missing permissions on specified dir {}".format(e))
        return

    config['root']['level'] = level
    if 'loggers' in config and utils.__find_route_module_name__() in config['loggers']:
        config['loggers'][utils.__find_route_module_name__()]['level'] = level

    # Create configuration
    logging.config.dictConfig(config)

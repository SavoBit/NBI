import os
import json


def load_schema(name):
    """
    Loads a schema in the current module's path
    :param name: The name of the schema to be loaded without the .JSON suffix
    :return: The json schema loaded and processed
    """
    module_path = os.path.dirname(__file__)
    path = os.path.join(module_path, '{}.json'.format(name))

    with open(os.path.abspath(path), 'r') as fp:
        data = fp.read()

    return json.loads(data)

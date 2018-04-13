from falcon.uri import parse_query_string


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


def __find_route_module_name__():
    return __name__.split(".", 1)[0]


def parse_multiple_parameters(req, resp, resource, params):
    """
    Parse query string and split into search_by and filter.
    Search by applies the criteria search
    Filter applies the fields to be replied
    :return: Dict in request parameter set as query_context
    """
    query_params = parse_query_string(req.query_string)
    req.context['query_parameters'] = query_params
    req.query_context = dict()

    req.query_context['search_by'] = \
        __parse_search__(query_params.get('search_by')) if 'search_by' in query_params else dict()

    req.query_context['filter'] = __parse_filter__(query_params.get('filter')) if 'filter' in query_params else []


def __parse_search__(query):
    """
    Parse the search by.
    First checks if a string is passed and converts = to : in order to later create a dictionary.
    If multiple parameters are provided a list is created otherwise the list will only contain one criteria.

    NOTE: This must be done because falcon parse the query parameters differently depending on the encoding.

    :param query: The query parameter parsed by falcon.
    :return: Dict with the search criteria
    """
    query = query.replace('=', ':').split(',') if isinstance(query, str) else [item.replace('=', ':') for item in query]
    if isinstance(query, str):
        query = [query]
    return dict(item.split(":") for item in query)


def __parse_filter__(query):
    """
    First checks if the provided query is a string and splits by comma to create a list, otherwise the list is used.

    NOTE: This must be done because falcon parse the query parameters differently depending on the encoding.

    :param query: The query parameter parsed by falcon
    :return: List with filter
    """
    query = query.split(',') if isinstance(query, str) else query
    if isinstance(query, str):
        query = [query]
    return query

import logging
import requests
from requests import post, patch, delete, get, put

from functools import wraps

from falcon import HTTPInternalServerError, HTTPError, HTTP_REQUEST_TIMEOUT, HTTP_INTERNAL_SERVER_ERROR, HTTPNotFound,\
    HTTPUnauthorized

from service.conf_reader import ConfReader

logger = logging.getLogger(__name__)


REQUEST_METHOD = {
    'POST': post,
    'PATCH': patch,
    'DELETE': delete,
    'GET': get,
    'PUT': put
}


def handle_exception(function):
    """
    Handles all exceptions from the requests performed.
    When a given response is higher than 299 an exception is raised with the same code
    :return:
    """
    @wraps(function)
    def __handle__(*args, **kwargs):
        """

        :param args:
        :param kwargs:
                        service_name: the name of the service that is using the requester
        :return: the response object if no error detected
        :raises:
                requests.exceptions.Timeout: when the timeout is reached
                requests.exceptions.ConnectionError: When no connection is available
        """
        service = kwargs.get('service_name', 'Service')
        if 'ignore_exception' in kwargs:
            r = function(*args, **kwargs)
            return r
        try:
            r = function(*args, **kwargs)
            if r.status_code == 401:
                raise HTTPUnauthorized(title='You are not authorized',
                                       description='Please validate your authentication')
            if r.status_code == 404:
                raise HTTPNotFound()
            if r.status_code == 500:
                raise HTTPInternalServerError('Failed to process request on {}'.format(service), code='102')
            if r.status_code > 299:
                raise HTTPError(str(r.status_code), description=r.text, code='103')
            return r
        except requests.exceptions.Timeout:
            logger.error('{} Timeout'.format(service))
            raise HTTPError(HTTP_REQUEST_TIMEOUT, title='{} Timeout'.format(service),
                            description='{} connection timeout'.format(service), code='100')
        except requests.exceptions.ConnectionError:
            raise HTTPError(HTTP_INTERNAL_SERVER_ERROR, title='{} Connection Error'.format(service),
                            description='{} connection error'.format(service), code='101')

    return __handle__


@handle_exception
def request(endpoint, method='GET', **kwargs):
    """
    Perform GET and DELETE requests to the given endpoint
    :param endpoint: The endpoint to perform the request
    :param method: The method to use
    :param kwargs:
                    headers: the request headers
                    params: the request query parameters
    :return: request response object
    """
    logger.debug('Requiring {} for {}, {}'.format(method, kwargs.get('service_name', 'Service'), endpoint))
    r_method = REQUEST_METHOD[method]
    r = r_method(
        endpoint,
        params=kwargs.get('params', {}),
        headers=kwargs.get('headers', {}),
        timeout=ConfReader().get('REQUESTER', 'timeout')
    )
    logger.debug('Response from {}: {}'.format(kwargs.get('service_name', 'Service'), r.text if r.text else None))
    return r


@handle_exception
def request_post_patch(endpoint, method, **kwargs):
    """
    Perform POST, PATCH and PUT requests to the given endpoint
    :param endpoint: The endpoint to perform the request
    :param method: The method to use
    :param kwargs:
                    headers: the request headers
                    json: the request object in a dict format
    :return: request response object
    """
    logger.info('Requiring {} for {}, {}'.format(method, kwargs.get('service_name', 'Service'), endpoint))
    r_method = REQUEST_METHOD[method]
    r = r_method(
        endpoint,
        json=kwargs.get('json'),
        headers=kwargs.get('headers', {}),
        timeout=ConfReader().get('REQUESTER', 'timeout')
    )
    logger.debug('Response from {}: {}'.format(kwargs.get('service_name', 'Service'), r.text if r.text else None))
    return r

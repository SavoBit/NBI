import logging
import requests

from functools import wraps

from falcon import HTTPInternalServerError, HTTPError, HTTP_REQUEST_TIMEOUT, HTTP_INTERNAL_SERVER_ERROR, HTTPNotFound

from service.conf_reader import ConfReader

logger = logging.getLogger(__name__)


def handle_exception(function):
    @wraps(function)
    def __handle__(*args, **kwargs):
        service = kwargs.get('service_name', 'Service')
        try:
            r = function(*args, **kwargs)
            if r.status_code == 404:
                raise HTTPNotFound()
            if r.status_code == 500:
                raise HTTPInternalServerError('Failed to process request on {}'.format(service), code='102')
            if r.status_code > 299:
                raise HTTPError(str(r.status_code))
            return r
        except requests.exceptions.Timeout:
            logger.error('{} Inventory Timeout'.format(service))
            raise HTTPError(HTTP_REQUEST_TIMEOUT, title='{} Timeout'.format(service),
                            description='{} connection timeout'.format(service), code='100')
        except requests.exceptions.ConnectionError:
            raise HTTPError(HTTP_INTERNAL_SERVER_ERROR, title='{} Connection Error'.format(service),
                            description='{} connection error'.format(service), code='101')
    return __handle__


@handle_exception
def request(endpoint, **kwargs):
    logger.info('Requiring {} Information, {}'.format(kwargs.get('service_name', 'Service'), endpoint))
    r = requests.get(endpoint, params=kwargs.get('params', {}), headers=kwargs.get('headers', {}),
                     timeout=ConfReader().get('REQUESTER', 'timeout'))
    logger.debug('Response from {}: {}'.format(kwargs.get('service_name', 'Service'), r.text if r.text else None))
    return r

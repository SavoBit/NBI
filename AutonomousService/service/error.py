import logging
from functools import wraps

from falcon import HTTPInternalServerError, HTTP_REQUEST_TIMEOUT, HTTPError
from pymongo.errors import ServerSelectionTimeoutError

logger = logging.getLogger(__name__)


def handle_mongodb_exception(function):
    """
    Wrapper for mongo db operations.
    This decorator forces an Internal server error if anything occurs in Mongo
    """

    @wraps(function)
    def __handle__(*args, **kwargs):
        try:
            r = function(*args, **kwargs)
            return r
        except ServerSelectionTimeoutError:
            logger.error('DB Timeout')
            raise HTTPError(HTTP_REQUEST_TIMEOUT, title='DB Timeout',
                            description='DB connection timeout', code='100')
        except Exception as e:
            logger.exception('DB error')
            error = dict(title='Database Error')
            try:
                error['description'] = e.orig.msg
            except Exception:
                error['description'] = e.args[0]
            error['code'] = '105'
            raise HTTPInternalServerError(**error)

    return __handle__

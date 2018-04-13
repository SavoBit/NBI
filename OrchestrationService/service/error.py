import logging

from functools import wraps

from falcon import HTTPInternalServerError

logger = logging.getLogger(__name__)


def handle_topology_exception(function):
    @wraps(function)
    def __handle__(*args, **kwargs):
        try:
            r = function(*args, **kwargs)
            return r
        except Exception as e:
            logger.exception('DB error: Topology')
            error = dict(title='Topology: Database Error')
            try:
                error['description'] = e.orig.msg
            except Exception:
                error['description'] = e.args[0]
            error['code'] = '105'
            raise HTTPInternalServerError(**error)
    return __handle__


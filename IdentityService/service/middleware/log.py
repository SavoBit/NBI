import logging


class LogMiddleware(object):
    """
    Log all accesses to the platform
    """
    logger = logging.getLogger('access')

    def process_response(self, req, resp, resource):
        LogMiddleware.logger.info(
            'ID: {} | VERB: {} | URI: {} | RESP: {}'.format(
                resp.get_header('request-id'),
                req.method,
                req.relative_uri,
                resp.status[:3]
            )
        )

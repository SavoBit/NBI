import uuid


class ContextMiddleware(object):
    """
    Set a Context to each request.
    Set a response header to the request id
    """

    def process_request(self, req, resp, **kwargs):
        if not req.context.get('request_id'):
            req.context['request_id'] = str(uuid.uuid4())

        resp.set_header('request-id', req.context['request_id'])

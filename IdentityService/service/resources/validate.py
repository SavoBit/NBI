from falcon import HTTP_200


class ValidatorAPI(object):
    """
    API to validate incoming tokens
    """

    ROUTES = [
        'token/validate',
        'token/validate/'
    ]

    def on_get(self, req, resp):
        """
        Validates a token and provides a session obj
        :return:
                200 OK: Token Validated with success
        """
        data = req.context['auth']
        tenant = dict(id=data.get('domain_id', None), name=data.get('domain_name', None))
        role = dict(name=data.get('roles')[0])
        user = dict(id=data.get('user_id', None), name=data.get('user_name', None), tenant=tenant, role=role)
        data = dict(user=user)
        req.context['result'] = dict(session=data)
        resp.status = HTTP_200

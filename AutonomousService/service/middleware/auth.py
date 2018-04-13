class AuthMiddleware(object):
    """
    Headers set by the Keystone middleware framework
    """

    def process_request(self, req, resp):
        headers = req.headers
        user_name = headers.get('X-USER-NAME')
        user_id = headers.get('X-USER-ID')
        project = headers.get('X-PROJECT-NAME')
        project_id = headers.get('X-PROJECT-ID')
        domain_id = headers.get('X-USER-DOMAIN-ID')
        domain_name = headers.get('X-USER-DOMAIN-NAME')
        auth_token = headers.get('X-AUTH-TOKEN')
        roles = headers.get('X-ROLES', '').split(',')

        req.context['auth'] = dict(
            auth_token=auth_token,
            user_name=user_name,
            user_id=user_id,
            project_name=project,
            project_id=project_id,
            tenant_id=domain_id,  # Map to SELFNET values
            tenant_name=domain_name,  # Map to SELFNET values
            roles=roles)

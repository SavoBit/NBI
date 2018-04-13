from functools import wraps
from falcon import HTTPForbidden
from oslo_policy import policy
from oslo_config import cfg


class Policy(object):
    """
    Class that validates the actions over a given resource, using oslo_policy
    """
    ENFORCER = None

    @staticmethod
    def load_enforcer():
        """
        Dynamically load the policy file rules
        """
        Policy.ENFORCER = policy.Enforcer(cfg.CONF, policy_file='policy.json')

    @staticmethod
    def exception():
        """
        The exception that will be raised when no authz is given.
        """
        raise HTTPForbidden("Permission Denied", "You Are not allowed to consume this resource")


def enforce(scope, name):
    def outer(f):
        @wraps(f)
        def wrapped(self, req, resp, *args, **kwargs):
            """
            Decorator to be used with methods. The function argument's are directly related to the Falcon framework,
            that by default demands the req and resp arguments.
            """
            check_policy(req, name, scope, target=kwargs)
            return f(self, req, resp, *args, **kwargs)
        return wrapped
    return outer


def check_policy(req, action, scope, target=None):
    """
    Enforce a given policy. This function is auxiliary to the decorator enforce.
    This will write the action in the correct format, based on the scope and action.
    This must be mapped according to the policy.json file.
    :param req: The request object that contains the context dictionary with all headers from token
    :param action: The action that will be performed over a given scope
    :param scope: The scope of the action
    :param target: The target object that will be evaluated, sent by kwargs within url.
    """
    action = '{0}:{1}'.format(scope, action)  # Creates the action in the correct format
    if not Policy.ENFORCER:
        Policy.load_enforcer()
    extra = {}
    extra.update(exc=Policy.exception, do_raise=True)
    auth = req.context.get('auth')  # oslo_policy creds
    target = target if target else {}
    return Policy.ENFORCER.enforce(action, target, auth, **extra)

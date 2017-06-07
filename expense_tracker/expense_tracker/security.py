"""Security configuration for our Pyramid application."""
import os
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Everyone, Authenticated, Allow
from pyramid.session import SignedCookieSessionFactory
from passlib.apps import custom_app_context as context


class MyRoot(object):

    def __init__(self, request):
        self.request = request

    __acl__ = [
        (Allow, Authenticated, 'secret')
    ]


def check_credentials(username, password):
    """Checks credentials of a new user.

    Return True if it checks out; otherwise return False."""
    stored_username = os.environ.get('AUTH_USERNAME', '')
    stored_password = os.environ.get('AUTH_PASSWORD', '')
    is_authenticated = False
    if stored_username and stored_password:
        if username == stored_username:
            if context.verify(password, stored_password):
                is_authenticated = True
    return is_authenticated


def includeme(config):
    """Configuration for security."""
    auth_secret = os.environ.get('AUTH_SECRET', '')
    authn_policy = AuthTktAuthenticationPolicy(
        secret=auth_secret,
        hashalg='sha512'
    )
    config.set_authentication_policy(authn_policy)
    authz_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authz_policy)
    config.set_root_factory(MyRoot)

    session_secret = os.environ.get('SESSION_SECRET')
    session_factory = SignedCookieSessionFactory(session_secret)
    config.set_session_factory(session_factory)
    config.set_default_csrf_options(require_csrf=True)

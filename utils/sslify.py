# -*- coding: utf-8 -*-

from flask import request, redirect, current_app, make_response

YEAR_IN_SECS = 31536000


class SSLify(object):
    """Secures your Flask App."""

    def __init__(self, app=None, age=YEAR_IN_SECS, subdomains=False, permanent=False, skips=None, no_redirects=None,
                 no_redirect_message=None, no_redirect_code=None):
        self.app = app or current_app
        self.hsts_age = age

        self.app.config.setdefault('SSLIFY_SUBDOMAINS', False)
        self.app.config.setdefault('SSLIFY_PERMANENT', False)
        self.app.config.setdefault('SSLIFY_SKIPS', None)
        self.app.config.setdefault('SSLIFY_NO_REDIRECTS', None)
        self.app.config.setdefault('SSLIFY_NO_REDIRECT_MESSAGE', "Endpoint must be reached via https.")
        self.app.config.setdefault('SSLIFY_NO_REDIRECT_CODE', 400)

        self.hsts_include_subdomains = subdomains or self.app.config['SSLIFY_SUBDOMAINS']
        self.permanent = permanent or self.app.config['SSLIFY_PERMANENT']
        self.skip_list = skips or self.app.config['SSLIFY_SKIPS']
        self.no_redirect_list = no_redirects or self.app.config['SSLIFY_NO_REDIRECTS']
        self.no_redirect_message = no_redirect_message or self.app.config['SSLIFY_NO_REDIRECT_MESSAGE']
        self.no_redirect_code = no_redirect_code or self.app.config['SSLIFY_NO_REDIRECT_CODE']

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Configures the configured Flask app to enforce SSL."""
        app.before_request(self.redirect_to_ssl)
        app.after_request(self.set_hsts_header)

    @property
    def hsts_header(self):
        """Returns the proper HSTS policy."""
        hsts_policy = 'max-age={0}'.format(self.hsts_age)

        if self.hsts_include_subdomains:
            hsts_policy += '; includeSubDomains'

        return hsts_policy

    @property
    def skip(self):
        """Checks the skip list."""
        # Should we skip?
        if self.skip_list and isinstance(self.skip_list, list):
            for skip in self.skip_list:
                if request.path.startswith('/{0}'.format(skip)):
                    return True
        return False

    @property
    def no_redirect(self):
        """Checks the no_redirect list. Useful for API's that want to encourge use of HTTPS only"""
        if self.no_redirect_list and isinstance(self.no_redirect_list, list):
            for no_redirect in self.no_redirect_list:
                if request.path.startswith('/{0}'.format(no_redirect)) \
                        or request.script_root.startswith('/{0}'.format(no_redirect)):
                    return True
            return False

    def redirect_to_ssl(self):
        """Redirect incoming requests to HTTPS."""
        # Should we redirect?
        criteria = [
            request.is_secure,
            current_app.debug,
            current_app.testing,
            request.headers.get('X-Forwarded-Proto', 'http') == 'https'
        ]

        if not any(criteria) and not self.skip:
            # ensure path is not a no_redirect, return error response if endpoint is in list.
            if self.no_redirect:
                r = make_response(self.no_redirect_message)
                r.status_code = self.no_redirect_code
                return r
            if request.url.startswith('http://'):
                url = request.url.replace('http://', 'https://', 1)
                code = 302
                if self.permanent:
                    code = 301
                r = redirect(url, code=code)
                return r

    def set_hsts_header(self, response):
        """Adds HSTS header to each response."""
        # Should we add STS header?
        if request.is_secure and not self.skip:
            response.headers.setdefault('Strict-Transport-Security', self.hsts_header)
        return response

from urllib.parse import urlencode

import requests
from django.conf import settings

from accounts.erros import TokenRequestFailed

CONFIG = settings.ACCOUNTS_SETTINGS.get('google', {})


class GoogleProvider:
    TOKEN_URI = 'https://www.googleapis.com/oauth2/v4/token'
    PROFILE_URI = 'https://www.googleapis.com/oauth2/v1/userinfo'
    AUTHORIZE_URI = 'https://accounts.google.com/o/oauth2/v2/auth'

    def __init__(self):
        self.request = None
        self.redirect_uri = CONFIG.get('redirect_uri', '/')
        self.client_id = CONFIG.get('client_id', '')
        self.client_secret = CONFIG.get('secret', '')
        self.grant_type = 'authorization_code'
        self.response_type = 'code'
        self.access_type = 'offline'
        self.scope = 'https://www.googleapis.com/auth/userinfo.email'


class GoogleProviderToken(GoogleProvider):

    def get_token(self):
        code = self.request.GET.dict().get('code', '')
        host = f'{self.request.scheme}://{self.request.get_host()}'

        resp = requests.post(self.TOKEN_URI, data={
            'grant_type': self.grant_type,
            'code': code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': f'{host}{self.redirect_uri}',
        })
        if resp.status_code == 200:
            return resp.json()
        raise TokenRequestFailed


class GoogleProviderLogin(GoogleProvider):

    def get_redirect_url(self):
        host = self.request.build_absolute_uri().replace(self.request.path, '')
        query = urlencode({
            'client_id': self.client_id,
            'redirect_uri': f"{host}{self.redirect_uri}",
            'scope': self.scope,
            'response_type': self.response_type,
            'include_granted_scopes': 'true',
            'access_type': self.access_type,
        })
        return f"{self.AUTHORIZE_URI}?{query}"

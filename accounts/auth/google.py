import requests
from django.conf import settings
from urllib.parse import urlencode
from django.contrib.auth import get_user_model
from accounts.models import RefreshTokens
from accounts.auth.token import JSONWebToken

CONFIG = settings.ACCOUNTS_SETTINGS.get('google', {})


class TokenRequestFailed(Exception):

    def __str__(self):
        return 'Google get token load failed ...'


class ProfileRequestFailed(Exception):

    def __str__(self):
        return 'Google get profile information load failed...'


class NotFoundIDToken(Exception):

    def __str__(self):
        return 'Not Found Google ID Token ...'


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


class GoogleProviderCallback(GoogleProviderToken, JSONWebToken):

    def __init__(self, function):
        super(GoogleProviderCallback, self).__init__()
        self.func = function

    def __call__(self, request, *args, **kwargs):
        self.request = request

        query_string = self.save()
        redirect_url = f"{settings.LOGIN_REDIRECT_URL}?{query_string}"

        kwargs.update({'redirect_url': redirect_url})
        dispatch = self.func(request, *args, **kwargs)
        return dispatch

    @staticmethod
    def save_refresh_token(token: str):
        RefreshTokens.objects.update_or_create(
            refresh_token=token,
            defaults={'refresh_token': token}
        )

    @staticmethod
    def save_user(profiles: dict) -> dict:
        defaults = {
            'uid': profiles.get('sub', ''),  # google user id
            'nickname': profiles.get('name', ''),
            'locale': profiles.get('locale', ''),
            'picture': profiles.get('picture', ''),
        }
        obj, _ = get_user_model().objects.update_or_create(
            email=profiles.get('email', ''),
            defaults=defaults
        )
        defaults.update({'id': obj.id})
        return defaults

    def save(self) -> str:
        tokens = self.get_token()
        id_token = tokens.get('id_token', '')
        if not id_token:
            raise NotFoundIDToken

        profiles = self.extra_data(id_token)
        defaults: dict = self.save_user(profiles)

        access_token = self._access_token(**{'uid': defaults.get('id', 0)})
        refresh_token = self._refresh_token()
        self.save_refresh_token(refresh_token)

        return urlencode({
            **defaults,
            'email': profiles.get('email', ''),
            'accessToken': access_token,
            'refreshToken': refresh_token,
        })

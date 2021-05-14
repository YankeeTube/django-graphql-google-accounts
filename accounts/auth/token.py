import jwt
from django.conf import settings
from django.utils import timezone
from django.core.management.utils import get_random_secret_key

SECRET_KEY = settings.ACCOUNTS_SETTINGS.get('token_secret', '')
CLAIM = settings.ACCOUNTS_SETTINGS.get('claim', {})


class TokenTime:

    def __call__(self, *args, **kwargs):
        delta = kwargs.get('exp', 1800)
        iat = timezone.now()
        exp = iat + timezone.timedelta(seconds=delta)  # default 5 minutes
        return int(iat.timestamp()), int(exp.timestamp())


class JWTWithoutSignature:

    @staticmethod
    def extra_data(token: str) -> dict:
        return jwt.decode(token, options={'verify_signature': False})


class JWTMakeToken:
    """
    [RFC-7519] - Registered Claim Names
    https://datatracker.ietf.org/doc/html/rfc7519#section-4.1

    [Google Authenticate] - Use ID Token
    https://cloud.google.com/endpoints/docs/openapi/authenticating-users-google-id?hl=ko#before_you_begin

    [IBM JWT for OAuth] - Claims in a JSON Web Token
    https://www.ibm.com/docs/en/was-liberty/base?topic=uocpao2as-json-web-token-jwt-oauth-client-authorization-grants#cwlp_jwttoken__claims_jwt
    """

    @staticmethod
    def _access_token(**kwargs) -> str:
        iat, exp = TokenTime().__call__(**{'exp': CLAIM.get('exp', 1800)})
        claim = {
            'iss': CLAIM.get('iss', 'django'),  # Issuer / 발급자
            'sub': CLAIM.get('sub', ''),  # Subject / 제목
            'aud': CLAIM.get('aud', ''),  # Audience / 대상
            'exp': exp,  # Expiration Time / 만료 시간(unix timestamp)
            'iat': iat,  # Issued At / 발급 시간
            **kwargs,
        }
        return jwt.encode(claim, key=SECRET_KEY, algorithm='HS256')

    @staticmethod
    def _refresh_token() -> str:
        """
        !Django Secret Key!
        [example]: https://djecrety.ir/
        """
        return get_random_secret_key()


class JSONWebToken(JWTMakeToken, JWTWithoutSignature):

    def __str__(self):
        return 'JSON Web Token Management'

    @classmethod
    def get_info_token(cls, info: object) -> dict:
        if not info:
            return {}

        bearer_token = info.context.META.get('HTTP_AUTHORIZATION', '')
        _token = bearer_token.split('Bearer ')
        if len(_token) == 1:
            return {}

        return cls.extra_data(_token[1])

from django.utils import timezone

from accounts.auth.token import JSONWebToken
from accounts.response import TOKEN_EXPIRE_RESPONSE, INVALID_SIGNATURE_RESPONSE


class VerifyTokenAuthenticate(JSONWebToken):
    """
    [Graphql Error Spec]
    https://www.apollographql.com/docs/apollo-server/data/errors/
    """

    def __init__(self, function):
        self.func = function

    def __call__(self, root, info, *args, **kwargs):
        result = self.func(root, info, *args, **kwargs)
        ctx = info.context

        token = self.has_token(ctx)
        if not token:
            return TOKEN_EXPIRE_RESPONSE

        if not self.check_signature(token):
            return INVALID_SIGNATURE_RESPONSE

        expire = self.expire_check(token)
        if not expire:
            return TOKEN_EXPIRE_RESPONSE

        have_not_user = self.has_user(token)
        if not have_not_user:
            return TOKEN_EXPIRE_RESPONSE
        return result  # success

    @classmethod
    def has_token(cls, context) -> str:
        bearer_token = context.META.get('HTTP_AUTHORIZATION', '')
        _token = bearer_token.split('Bearer ')
        return _token[-1]

    @classmethod
    def check_signature(cls, token: str):
        obj = cls._decode(token)
        if isinstance(obj, dict):
            return True
        return False

    @classmethod
    def expire_check(cls, token: str) -> bool:
        now = int(timezone.now().timestamp())
        exp = cls._decode(token).get('exp', 0)
        if exp <= now:
            return False
        return True

    @classmethod
    def has_user(cls, token: str) -> bool:
        uid = cls._decode(token).get('uid', 0)
        if uid == 0:
            return False
        return True

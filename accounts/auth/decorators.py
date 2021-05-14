from django.utils import timezone
from django.utils.decorators import method_decorator
from accounts.auth.token import JSONWebToken
from accounts.auth.google import GoogleProviderCallback
from accounts.response import ERROR_RESPONSE


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
            return ERROR_RESPONSE

        expire = self.expire_check(token)
        if not expire:
            return ERROR_RESPONSE

        have_not_user = self.has_user(token)
        if not have_not_user:
            return ERROR_RESPONSE
        return result  # success

    @classmethod
    def has_token(cls, context) -> str:
        bearer_token = context.META.get('HTTP_AUTHORIZATION', '')
        _token = bearer_token.split('Bearer ')
        return _token[-1]

    @classmethod
    def expire_check(cls, token: str) -> bool:
        now = int(timezone.now().timestamp())
        exp = cls.extra_data(token).get('exp', 0)
        if exp <= now:
            return False
        return True

    @classmethod
    def has_user(cls, token: str) -> bool:
        uid = cls.extra_data(token).get('uid', 0)
        if uid == 0:
            return False
        return True


"""
    Google Accounts Class Based Decorator Defined
"""
google_provider_callback_save = method_decorator(GoogleProviderCallback)
login_required = VerifyTokenAuthenticate

from django.utils import timezone
from django.utils.decorators import method_decorator
from accounts.auth.token import JSONWebToken
from accounts.auth.google import GoogleProviderCallback
from graphql import GraphQLError


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
            return result

        return self.expire_check(token, result)

    @classmethod
    def has_token(cls, context):
        bearer_token = context.META.get('HTTP_AUTHORIZATION', '')
        _token = bearer_token.split('Bearer ')
        return _token[-1]

    @classmethod
    def expire_check(cls, token: str, result):
        now = int(timezone.now().timestamp())
        exp = cls.extra_data(token).get('exp', 0)
        if exp <= now:
            return GraphQLError('AuthenticationError', extensions={
                'code': 401,
                'name': 'UNAUTHENTICATED',
                'message': 'Authentication Error',
            })
        return result


"""
    Google Accounts Class Based Decorator Defined
"""
google_provider_callback_save = method_decorator(GoogleProviderCallback)
login_required = VerifyTokenAuthenticate

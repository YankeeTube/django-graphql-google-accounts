from django.utils.decorators import method_decorator

from accounts.decorators.google import GoogleProviderCallback
from accounts.decorators.token import VerifyTokenAuthenticate

"""
    Google Accounts Class Based Decorator Defined
"""
google_provider_callback_save = method_decorator(GoogleProviderCallback)
login_required = VerifyTokenAuthenticate

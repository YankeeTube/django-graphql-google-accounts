from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.core.exceptions import ObjectDoesNotExist


class GoogleAuthBackend(BaseBackend):
    model = get_user_model()

    def authenticate(self, request, email=None):
        if not email:
            return None

        try:
            user = self.model.objects.get(email=email)
            return user
        except ObjectDoesNotExist:
            return None
        except Exception as e:
            print(str(e))
            return None

    def get_user(self, uid):
        try:
            return self.model.objects.get(pk=uid)
        except ObjectDoesNotExist:
            return None
        except Exception as e:
            print(str(e))
            return None

from django.contrib.auth import get_user_model

class AuthenticationBackendAnonymous:
    def authenticate(self, username=None, password=None, anonymus=False):
        # make sure they have a profile and that they are anonymous
        # if you're not using profiles you can just return user
        if anonymus:
            try:
                return get_user_model().objects.get(email=username)
            except get_user_model().DoesNotExist:
                return None

    def get_user(self, user_id):
        try:
            return get_user_model().objects.get(pk=user_id)
        except get_user_model().DoesNotExist:
            return None

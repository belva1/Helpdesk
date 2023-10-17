from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions
from django.utils import timezone


class HelpdeskTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        model = self.get_model()  # model with tokens
        try:
            token = model.objects.get(key=key)  # instance of model
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Token does not exist.')

        if not token.user.is_authenticated:
            raise exceptions.AuthenticationFailed('User is not authenticated.')
        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User is not active.')

        if not token.user.is_superuser and (timezone.now() - token.created).total_seconds() > 60:
            token.delete()
            raise exceptions.AuthenticationFailed('Token was deleted after 1 min of inactivity.')
        token.created = timezone.now()
        token.save()
        return token.user, token

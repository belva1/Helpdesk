from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions
from django.utils import timezone


class HelpdeskTokenAuthentication(TokenAuthentication):
    def get_model(self):
        if self.model is not None:
            return self.model
        from rest_framework.authtoken.models import Token
        return Token

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Token does not exist.')

        user = token.user
        if not user.is_authenticated:
            raise exceptions.AuthenticationFailed('User is not authenticated.')

        if not user.is_active:
            raise exceptions.AuthenticationFailed('User is not active.')

        if not user.is_superuser:
            if (timezone.now() - token.created).total_seconds() > 60:
                token.delete()
                raise exceptions.AuthenticationFailed('Token was deleted after 1 min of inactivity.')
            token.created = timezone.now()
            token.save()

        return user, token

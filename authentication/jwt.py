from rest_framework.authentication import (get_authorization_header, BaseAuthentication)
from rest_framework import exceptions
import jwt
from django.conf import settings
from authentication.models import User


class JWTAuthentication(BaseAuthentication):

    def authenticate(self, request):
        auth_token = get_authorization_header(request).decode('utf-8').split(' ')
        if len(auth_token) != 2:
            raise exceptions.AuthenticationFailed('Token not valid!')
        token = auth_token[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
            user = User.objects.get(email=payload['email'])
            return (user, token)
        except jwt.ExpiredSignatureError as ex:
            raise exceptions.AuthenticationFailed('Token is expired, login again!')
        except jwt.DecodeError as ex:
            raise exceptions.AuthenticationFailed('Token is invalid!')
        except User.DoesNotExist as no_user:
            raise exceptions.AuthenticationFailed('No such user!')

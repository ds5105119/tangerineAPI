import copy

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.functional import LazyObject
from jwt import decode as jwt_decode
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


@database_sync_to_async
def get_user(authorization):
    from django.contrib.auth.models import AnonymousUser
    from rest_framework_simplejwt.tokens import AccessToken

    if not authorization:
        raise ValueError(
            "Cannot find authorization header in scope. You should wrap your consumer in " "JWTMiddleWare."
        )

    user = None

    try:
        token_type, token = authorization.decode().split()
    except ValueError as e:
        raise e

    try:
        AccessToken(token)
        decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user = get_user_model().objects.get(handle=decoded_data["user_id"])
    except (InvalidToken, TokenError, UnicodeDecodeError, ValueError):
        pass
    return user or AnonymousUser()


class UserLazyObject(LazyObject):
    """
    Throw a more useful error message when scope['user'] is accessed before
    it's resolved
    """

    def _setup(self):
        raise ValueError("Accessing scope user before it is ready.")


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        scope_copy = copy.deepcopy(scope)

        try:
            # Verify headers exist
            if "headers" not in scope_copy:
                raise ValueError("AuthMiddleware cannot find headers in scope.")

            headers = dict(scope_copy["headers"])
            authorization = headers.get(b"authorization")

            if not authorization:
                raise ValueError("AuthMiddleware cannot find authorization in headers.")

            # Initialize user if not present
            if "user" not in scope_copy:
                scope_copy["user"] = UserLazyObject()

            # Resolve user
            user = await get_user(authorization)
            scope_copy["user"]._wrapped = user

            return await super().__call__(scope_copy, receive, send)

        except Exception as e:
            # Log the error if you have logging configured
            print(f"Error in JWTAuthMiddleware: {str(e)}")
            # You might want to handle different types of errors differently
            return await super().__call__(scope, receive, send)

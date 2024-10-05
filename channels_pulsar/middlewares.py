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
    def populate_scope(self, scope):
        # Make sure we have a session
        if "headers" not in scope:
            raise ValueError("AuthMiddleware cannot find header in scope. " "JWTMiddleware must be above it.")
        if b"authorization" not in dict(scope["headers"]):
            raise ValueError("AuthMiddleware cannot find authorization in header. " "JWTMiddleware must be above it.")
        # Add it to the scope if it's not there already
        if "user" not in scope:
            scope["user"] = UserLazyObject()

    async def resolve_scope(self, scope):
        scope["user"]._wrapped = await get_user(dict(scope["headers"])[b"authorization"])

    async def __call__(self, scope, receive, send):
        scope = dict(scope)
        # Scope injection/mutation per this middleware's needs.
        self.populate_scope(scope)
        # Grab the finalized/resolved scope
        await self.resolve_scope(scope)

        return await super().__call__(scope, receive, send)

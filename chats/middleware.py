from channels.middleware import BaseMiddleware
from rest_framework_simplejwt.tokens import AccessToken
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs
from django.contrib.auth.models import AnonymousUser

User = get_user_model()


class JWTAuthMiddleware(BaseMiddleware):
    """
    Middleware accepts token either in:
      - Authorization header: "Bearer <token>" (useful for wscat/postman)
      - Querystring: ?token=<access_token> (useful for browser ws)
    """

    async def __call__(self, scope, receive, send):
        scope = dict(scope)
        scope.setdefault("user", AnonymousUser())
        scope.setdefault("auth_error", None)

        token = self._get_token_from_scope(scope)

        if token:
            user = await self.get_user_from_token(token)
            if user:
                scope["user"] = user
            else:
                scope["auth_error"] = "Invalid token or user not found."
        else:
            scope["auth_error"] = "No token provided."

        # call parent to continue normal middleware chain
        return await super().__call__(scope, receive, send)

    def _get_token_from_scope(self, scope):
        headers = dict(scope.get("headers", []))
        auth_header = headers.get(b"authorization", b"").decode("utf-8")
        if auth_header:
            if auth_header.lower().startswith("bearer "):
                return auth_header.split(" ", 1)[1]

        qs_raw = scope.get("query_string", b"").decode()
        qs = parse_qs(qs_raw)
        token = qs.get("token", [None])[0] or qs.get("access", [None])[0]
        if token:
            if token.lower().startswith("bearer "):
                token = token.split(" ", 1)[1]
            return token

        return None

    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            access = AccessToken(token)
            user_id = access.get("user_id") or access.get("user") or access.get("id")
            if not user_id:
                return None
            UserModel = get_user_model()
            try:
                return UserModel.objects.get(id=user_id)
            except UserModel.DoesNotExist:
                return None
        except Exception:
            return None

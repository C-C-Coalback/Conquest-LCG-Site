from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from rest_framework.authtoken.models import Token

@database_sync_to_async
def get_user_from_token(token_key):
    try:
        return Token.objects.select_related("user").get(key=token_key).user
    except Token.DoesNotExist:
        return None

class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = parse_qs(scope["query_string"].decode())
        token_key = query_string.get("token", [None])[0]

        if token_key:
            user = await get_user_from_token(token_key)
            if user is not None:
                scope["user"] = user
            # if token is invalid, fall through and keep whatever
            # AuthMiddlewareStack already put in scope["user"]

        return await super().__call__(scope, receive, send)

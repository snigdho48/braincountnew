from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async

@database_sync_to_async
def get_user(validated_token):
    from rest_framework_simplejwt.authentication import JWTAuthentication
    from django.contrib.auth.models import AnonymousUser

    try:
        jwt_auth = JWTAuthentication()
        user = jwt_auth.get_user(validated_token)
        return user
    except Exception:
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        from rest_framework_simplejwt.tokens import UntypedToken
        from django.contrib.auth.models import AnonymousUser

        query_string = scope['query_string'].decode()
        token = parse_qs(query_string).get('token')

        if token:
            token = token[0]
            try:
                validated_token = UntypedToken(token)
                scope['user'] = await get_user(validated_token)
            except Exception:
                scope['user'] = AnonymousUser()
        else:
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)

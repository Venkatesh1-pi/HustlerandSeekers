from urllib.parse import parse_qs
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from rest_framework.authtoken.models import Token
from channels.middleware import BaseMiddleware

@database_sync_to_async
def get_user(token_key):
    try:
        token = Token.objects.get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()

class TokenAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        token_key = None

        # Check Authorization header first
        if b'authorization' in headers:
            auth_header = headers[b'authorization'].decode()
            parts = auth_header.split()
            if len(parts) == 2 and parts[0] == 'Token':
                token_key = parts[1]

        # If no token in header, check query string
        if not token_key:
            query_string = scope.get('query_string', b'').decode()
            query_params = parse_qs(query_string)
            token_list = query_params.get('token')
            if token_list:
                token_key = token_list[0]

        if token_key:
            scope['user'] = await get_user(token_key)
        else:
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)

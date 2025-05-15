import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hustler.settings')
django.setup()  # <-- ADD THIS LINE to initialize apps before imports below

from channels.routing import URLRouter, ProtocolTypeRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from hustler_role_category import routing
from .tokenauth_middleware import TokenAuthMiddleware

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        TokenAuthMiddleware(URLRouter(routing.websocket_urlpatterns))
    ),
})

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'braincountBackend.settings')

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from api.middleware import JWTAuthMiddleware  # Use custom JWT middleware
import api.routing


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        URLRouter(
            api.routing.websocket_urlpatterns
        )
    ),
})

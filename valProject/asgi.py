import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import valProject.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valProject.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            valProject.routing.websocket_urlpatterns
        )
    ),
})
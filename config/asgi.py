import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Import handlers to ensure they are registered
import alerts.liveview_components.alerts  # noqa: F401

from liveview.consumers import LiveViewConsumer

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path('ws/liveview/<str:room_name>/', LiveViewConsumer.as_asgi()),
        ])
    ),
})

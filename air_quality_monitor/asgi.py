"""
ASGI config for DADN project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from api.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'air_quality_monitor.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # still supports HTTP if needed
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})

if __name__ == "__main__":
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync  # if calling from sync context

    def notify_warning_clients(message):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "warning_group",
            {
                "type": "send_warning",  # this maps to the send_warning() method above
                "message": message,
            }
        )

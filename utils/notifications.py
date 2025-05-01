from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def notify_warning_clients(message, typ):
    channel_layer = get_channel_layer()
    if channel_layer is not None:
        async_to_sync(channel_layer.group_send)(
            "warning_group",
            {
                "type": "send_warning",
                "typ": typ,
                "message": message,
            }
        )
    else:
        print("Channel layer is not available!")

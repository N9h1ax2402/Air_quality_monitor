from django.core.management.base import BaseCommand
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from ..utils.notifications import notify_warning_clients 

class Command(BaseCommand):
    help = 'Send a warning message to all WebSocket clients'

    def add_arguments(self, parser):
        parser.add_argument('message', type=str)

    def handle(self, *args, **options):
        message = options['message']
        typ = "warning"
        notify_warning_clients(message, typ)
        self.stdout.write(self.style.SUCCESS(f"Sent: {message}"))

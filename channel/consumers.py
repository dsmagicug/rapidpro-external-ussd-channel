import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class LiveSessionsConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_name = 'sessions'

    def connect(self):
        # Join  group
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave  group
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        sessions = text_data_json
        # Send message to group
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'report_sessions',
                'sessions': sessions
            }
        )

    def report_sessions(self, event):
        sessions = event['sessions']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'sessions': sessions
        }))

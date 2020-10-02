import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class PushConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = 'demo'
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
        command = text_data_json
        # Send message to group
        print("we are printing")
        print(command)
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'send_push',
                'command': command
            }
        )

    def send_push(self, event):
        command = event['command']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'command': command
        }))

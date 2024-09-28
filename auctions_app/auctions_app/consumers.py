from channels.generic.websocket import AsyncWebsocketConsumer
import json

class AuctionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.auction_id = self.scope['url_route']['kwargs']['auction_id']
        self.room_group_name = f'auction_{self.auction_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'auction_bid',
                'message': message
            }
        )

    async def auction_bid(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))


# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer

class PingConsumer(AsyncWebsocketConsumer):
    async def ping_message(self, event):
        # This is a test message type handler for Redis pinging
        pass

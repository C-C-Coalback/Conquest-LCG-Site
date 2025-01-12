import json

from channels.generic.websocket import AsyncWebsocketConsumer


chat_messages = [[], []]


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        global chat_messages
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        self.user = self.scope["user"]

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()
        print(self.room_name)
        for i in range(len(chat_messages[0])):
            if chat_messages[0][i] == self.room_name:
                await self.send(text_data=json.dumps({"message": chat_messages[1][i]}))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        global chat_messages
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        print("receive:", message)
        chat_messages[0].append(self.room_name)
        chat_messages[1].append(message)
        print(chat_messages)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        print("send:", message)
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))

import json
import os

from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        self.user = self.scope["user"]
        self.name = self.user.username
        print("username:", self.user.username, ".")
        if self.name == "":
            self.name = "Anonymous"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()
        print(self.room_name)
        room_logs_path = os.path.join(os.getcwd(), "chat/chat_logs/" + self.room_name)
        if os.path.exists(room_logs_path):
            with open(room_logs_path, "r") as logs_file:
                logs_text = logs_file.read()
            logs_split = logs_text.split(sep="\n")
            if len(logs_split) > 50:
                logs_split = logs_split[-50:]
            for i in range(len(logs_split)):
                if logs_split[i]:
                    await self.send(text_data=json.dumps({"message": logs_split[i]}))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        message = self.name + ": " + message
        message = message.replace("\n", "")
        print("receive:", message)
        room_logs_path = os.path.join(os.getcwd(), "chat/chat_logs/" + self.room_name)
        if not os.path.exists(os.path.join(os.getcwd(), "chat/chat_logs")):
            os.mkdir(os.path.join(os.getcwd(), "chat/chat_logs"))
        if os.path.exists(room_logs_path):
            with open(room_logs_path, "a") as logs_file:
                logs_file.write(message + "\n")
        else:
            with open(room_logs_path, "w") as logs_file:
                logs_file.write(message + "\n")
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

import json

from channels.generic.websocket import AsyncWebsocketConsumer


class InterviewConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.interview_code = self.scope["url_route"]["kwargs"]["interview_code"]
        self.channel_ident = f"chat_{self.interview_code}"
        await self.channel_layer.group_add(self.channel_ident, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.channel_ident, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        await self.channel_layer.group_send(
            self.channel_ident, {"type": "chat_message", "message": message}
        )

    async def chat_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))

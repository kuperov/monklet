import json

from channels.generic.websocket import AsyncWebsocketConsumer
from apps.projects.models import Interview


class InterviewConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("Connect")
        self.interview_code = self.scope["url_route"]["kwargs"]["interview_code"]
        self.channel_ident = f"chat_{self.interview_code}"
        await self.channel_layer.group_add(self.channel_ident, self.channel_name)
        await self.accept()
        print("accepted")

    async def disconnect(self, close_code):
        print(f"disconnect with code {close_code}")
        await self.channel_layer.group_discard(self.channel_ident, self.channel_name)
        print("disconnected")

    async def receive(self, text_data):
        print(f"receive text_data = {text_data}")
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        await self.channel_layer.group_send(
            self.channel_ident, {"type": "chat_message", "message": message}
        )
        print(f"message = {message}")
        interview = await Interview.objects.select_related('bot').aget(pk=self.interview_code)
        resp = await interview.add_user_message_async(message)
        print(f"resp = {resp}")
        await self.send(text_data=json.dumps(resp))
        print("sent response")

    async def chat_message(self, event):
        print(f"chat message event={event}")
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))
        print("sent.")

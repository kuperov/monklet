import json

from channels.generic.websocket import AsyncWebsocketConsumer
from apps.projects.models import Interview


class InterviewConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.interview_code = self.scope["url_route"]["kwargs"]["interview_code"]
        self.channel_ident = f"chat_{self.interview_code}"
        await self.channel_layer.group_add(self.channel_ident, self.channel_name)
        await self.accept()
        # does the interview need to be initialized? if not the user will see existing chat messages
        # by this point the user should be consuming the web socket and able to receive messages
        interview = await Interview.objects.aget(pk=self.interview_code)
        if interview.status == 'invited':  # uninitialized
            first = await interview.start_async()  # calls llm api, so takes a while
            await self.channel_layer.group_send(
                self.channel_ident, {"type": "chat_message", "message": first['message'], "sender": first['sender']}
            )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.channel_ident, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        await self.channel_layer.group_send(
            self.channel_ident, {"type": "chat_message", "message": message, "sender": "user"}
        )
        interview = await Interview.objects.aget(pk=self.interview_code)
        resp = await interview.add_user_message_async(message)
        await self.channel_layer.group_send(
            self.channel_ident, {"type": "chat_message", "message": resp['message'], "sender": resp['sender']}
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({"message": event["message"], "sender": event["sender"]}))

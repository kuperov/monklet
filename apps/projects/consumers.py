import json
import uuid

from django.utils.timezone import now
from channels.generic.websocket import AsyncWebsocketConsumer
from apps.projects.models import Interview


class InterviewConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.interview_code = self.scope["url_route"]["kwargs"]["interview_code"]
        self.channel_ident = f"chat_{self.interview_code}"
        await self.channel_layer.group_add(self.channel_ident, self.channel_name)
        await self.accept()
        # initialize interview if required
        interview = await Interview.objects.aget(pk=self.interview_code)
        if interview.status == "invited":  # uninitialized
            first = await interview.start_async()  # calls llm api, so takes a while
            await self.channel_layer.group_send(
                self.channel_ident,
                {
                    "type": "chat_message",
                    "message": first["message"],
                    "sender": first["sender"],
                    "sent_at": str(now()),
                    "uuid": str(uuid.uuid4()),
                },
            )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.channel_ident, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        await self.channel_layer.group_send(
            self.channel_ident,
            {
                "type": "chat_message",
                "message": message,
                "sender": "user",
                "sent_at": str(now()),
                "uuid": text_data_json["uuid"],
            },
        )
        interview = await Interview.objects.aget(pk=self.interview_code)
        resp = await interview.add_user_message_async(message)
        await self.channel_layer.group_send(
            self.channel_ident,
            {
                "type": "chat_message",
                "message": resp["message"],
                "sender": resp["sender"],
                "sent_at": str(now()),
                "uuid": str(uuid.uuid4()),
            },
        )
        if interview.status == "complete":
            await self.channel_layer.group_send(
                self.channel_ident,
                {
                    "type": "chat_message",
                    "message": "Interview complete",
                    "sender": "system",
                    "sent_at": str(now()),
                    "uuid": str(uuid.uuid4()),
                },
            )
            await self.disconnect(1000)

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "message": event["message"],
                    "sender": event["sender"],
                    "sent_at": event["sent_at"],
                    "uuid": event["uuid"],
                }
            )
        )

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Chat
from django.contrib.auth import get_user_model
from datetime import datetime
from asgiref.sync import sync_to_async
import base64, os
from uuid import uuid4
from django.conf import settings

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

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
        sender_id = data['sender_id']
        receiver_id = data['receiver_id']
        category_id = data.get('category_id')
        category_name = data.get('category_name')
        attachment = data.get('attachment')

        chat_id, created_at, attachment_url = await self.save_message(
            sender_id, receiver_id, message, category_id, category_name, attachment
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender_id,
                'receiver_id': receiver_id,
                'chat_id': chat_id,
                'created_at': created_at,
                'attachment': attachment_url
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def save_message(self, sender_id, receiver_id, message, category_id, category_name, attachment_b64):
        chat = Chat.objects.create(
            sender_id=sender_id,
            receiver_id=receiver_id,
            message=message,
            category_id=category_id,
            category_name=category_name,
            status="0",
        )

        attachment_url = ""
        if attachment_b64:
            try:
                file_data = base64.b64decode(attachment_b64)
                extension = "jpg"  # optionally detect using your existing `detect_file_type` function
                filename = f"{uuid4().hex}.{extension}"
                path = os.path.join(settings.MEDIA_ROOT, 'chat_attachments', filename)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'wb') as f:
                    f.write(file_data)
                chat.attachment = attachment_b64
                chat.save()
                attachment_url = f"{settings.MEDIA_URL}chat_attachments/{filename}"
            except Exception as e:
                print("Attachment error:", e)

        return chat.id, chat.created_at.strftime('%Y-%m-%d %I:%M %p'), attachment_url

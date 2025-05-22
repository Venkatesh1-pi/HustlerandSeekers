import json
import base64
import os
from uuid import uuid4
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from hustler_role_category.models import Chat
from django.conf import settings

User = get_user_model()
base_url = "http://82.25.86.49"

FILE_SIGNATURES = {
    'jpg': b'\xFF\xD8\xFF',
    'png': b'\x89\x50\x4E\x47',
    'gif': b'\x47\x49\x46\x38',
    'mp4': b'\x00\x00\x00\x18\x66\x74\x79\x70\x33\x67\x70\x35',
    'avi': b'\x52\x49\x46\x46',
    'pdf': b'\x25\x50\x44\x46',
    'doc': b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1',
    'docx': b'\x50\x4B\x03\x04',
    'ppt': b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1',
    'pptx': b'\x50\x4B\x03\x04',
}

def detect_file_type(file_bytes):
    for ext, signature in FILE_SIGNATURES.items():
        if file_bytes.startswith(signature):
            return ext
    return 'txt'

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = await self.get_user_from_token(self.scope)
        if not self.user or isinstance(self.user, AnonymousUser):
            await self.close()
            return

        self.room_group_name = f'chat_{self.user.id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)

            sender_id = str(data.get('sender_id'))
            if str(self.user.id) != sender_id:
                await self.send(json.dumps({
                    "type": "error",
                    "error_code": 403,
                    "error": "Permission denied."
                }))
                return

            chat = await self.save_chat_message(data)

            media_url = None
            if chat.attachment:
                media_url = base_url + settings.MEDIA_URL + chat.attachment

            response_data = {
                "type": "chat_message",
                "chat_id": chat.id,
                "created_at": chat.created_at.isoformat(),
                "sender_id": chat.sender_id,
                "receiver_id": chat.receiver_id,
                "message": chat.message,
                "attachment_url": media_url,
            }

            receiver_room = f'chat_{chat.receiver_id}'
            await self.channel_layer.group_send(
                receiver_room,
                {
                    'type': 'chat_message',
                    'message': response_data
                }
            )

            # Echo the same message back to sender
            await self.send(json.dumps(response_data))

        except Exception as e:
            print(f"Receive error: {e}")
            await self.send(json.dumps({
                "type": "error",
                "error_code": 500,
                "error": "Internal server error"
            }))

    async def chat_message(self, event):
        await self.send(json.dumps(event['message']))

    @database_sync_to_async
    def save_chat_message(self, data):
        chat = Chat(
            category_id=data['category_id'],
            category_name=data['category_name'],
            sender_id=data['sender_id'],
            receiver_id=data['receiver_id'],
            message=data['message'],
            status='0'
        )
        if data.get('attachment'):
            try:
                decoded_file = base64.b64decode(data['attachment'])
                extension = detect_file_type(decoded_file)
                file_name = f"{uuid4().hex}.{extension}"
                media_path = os.path.join(settings.MEDIA_ROOT, 'chat_attachments', file_name)
                os.makedirs(os.path.dirname(media_path), exist_ok=True)
                with open(media_path, 'wb') as f:
                    f.write(decoded_file)
                chat.attachment = f'chat_attachments/{file_name}'
            except Exception as e:
                print(f"Attachment decoding failed: {e}")
                raise
        chat.save()
        return chat

    @database_sync_to_async
    def get_user_from_token(self, scope):
        try:
            headers = dict(scope.get('headers', []))
            auth_header = headers.get(b'authorization')
            if auth_header:
                auth_header_str = auth_header.decode()
                if auth_header_str.startswith('Token '):
                    token_key = auth_header_str.split(' ')[1]
                    token = Token.objects.select_related('user').get(key=token_key)
                    return token.user
        except Exception as e:
            print(f"Token authentication failed: {e}")
        return AnonymousUser()
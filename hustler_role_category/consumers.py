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
from django.db.models import Q
import binascii

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
                await self.send(text_data=json.dumps({
                    "error": {"error_code": 403, "error": "Permission denied."}
                }))
                return

            chat = await self.save_chat_message(data)
            receiver_room = f'chat_{chat.receiver_id}'
            media_url = ""

            if chat.attachment:
                try:
                    decoded_file = base64.b64decode(chat.attachment)
                    extension = detect_file_type(decoded_file)
                    file_name = f"{uuid4().hex}.{extension}"
                    media_path = os.path.join(settings.MEDIA_ROOT, 'chat_attachments', file_name)
                    os.makedirs(os.path.dirname(media_path), exist_ok=True)
                    with open(media_path, 'wb') as f:
                        f.write(decoded_file)
                    media_url = os.path.join(settings.MEDIA_URL, 'chat_attachments', file_name)
                except Exception as e:
                    print(f"Attachment processing failed: {e}")

            old_messages = await self.get_old_messages(chat.category_id, chat.sender_id, chat.receiver_id)

            response_data = {
                "chat_id": chat.id,
                "created_at": str(chat.created_at),
                "sender_id": chat.sender_id,
                "receiver_id": chat.receiver_id,
                "message": chat.message,
                "attachment": base_url + media_url if media_url else None,
                "previous_messages": old_messages,
            }

            await self.channel_layer.group_send(
                receiver_room,
                {
                    'type': 'chat_message',
                    'message': response_data
                }
            )

            await self.send(text_data=json.dumps({
                "status": 201,
                "msg": "Message saved and sent to receiver",
                "chat": response_data
            }))

        except Exception as e:
            print(f"Receive error: {e}")
            await self.send(text_data=json.dumps({
                "error": {"error_code": 500, "error": "Internal server error"}
            }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event['message']))

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
                base64.b64decode(data['attachment'], validate=True)
                chat.attachment = data['attachment']
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

    @database_sync_to_async
    def get_old_messages(self, category_id, sender_id, receiver_id):
        messages = Chat.objects.filter(
            category_id=category_id
        ).filter(
            Q(sender_id=sender_id, receiver_id=receiver_id) |
            Q(sender_id=receiver_id, receiver_id=sender_id)
        ).order_by('-created_at')[:10]

        result = []
        for m in reversed(messages):
            media_url = ""
            if m.attachment:
                try:
                    decoded_file = base64.b64decode(m.attachment)
                    extension = detect_file_type(decoded_file)
                    file_name = f"{uuid4().hex}.{extension}"
                    media_path = os.path.join(settings.MEDIA_ROOT, 'chat_attachments', file_name)
                    os.makedirs(os.path.dirname(media_path), exist_ok=True)
                    with open(media_path, 'wb') as f:
                        f.write(decoded_file)
                    media_url = os.path.join(settings.MEDIA_URL, 'chat_attachments', file_name)
                except Exception as e:
                    print(f"Attachment decoding failed (old msg): {e}")
            result.append({
                "chat_id": m.id,
                "created_at": str(m.created_at),
                "sender_id": m.sender_id,
                "receiver_id": m.receiver_id,
                "message": m.message,
                "attachment": base_url + media_url if media_url else None,
            })
        return result

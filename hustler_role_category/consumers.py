import json
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from hustler_role_category.models import Chat
import os
import base64
from uuid import uuid4
from django.conf import settings
import binascii
import requests

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
User = get_user_model()
base_url = "http://82.25.86.49"
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = await self.get_user_from_token(self.scope)

        if not self.user or isinstance(self.user, AnonymousUser):
            # Close connection if not authenticated
            await self.close()
            return

        # Unique group per user for private messaging
        self.room_group_name = f'chat_{self.user.id}'

        # Add this channel to the user-specific group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print(f"User {self.user.id} connected to group {self.room_group_name}")

    async def disconnect(self, close_code):
        # Remove from group on disconnect
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            print(f"User {self.user.id} disconnected from group {self.room_group_name}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            sender_id = str(data.get('sender_id'))

            # Verify the sender matches the authenticated user
            if str(self.user.id) != sender_id:
                await self.send(text_data=json.dumps({
                    "error": {"error_code": 403, "error": "Permission denied."}
                }))
                return

            # Save the chat message in DB
            chat = await self.save_chat_message(data)

            # Notify the receiver's group with message info
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
            print(media_url)
            await self.channel_layer.group_send(
                receiver_room,
                {
                    'type': 'chat_message',
                    'message': {
                        "chat_id": chat.id,
                        "created_at": str(chat.created_at),
                        "sender_id": chat.sender_id,
                        "receiver_id": chat.receiver_id,
                        "message": chat.message,
                        "attachment": base_url+media_url if media_url else None,
                    }
                }
            )

            # Optionally, send confirmation back to sender
            await self.send(text_data=json.dumps({
                "status": 201,
                "msg": "Message saved and sent to receiver",
                "chat_id": chat.id,
            }))

        except Exception as e:
            print(f"Receive error: {e}")
            await self.send(text_data=json.dumps({
                "error": {"error_code": 500, "error": "Internal server error"}
            }))

    async def chat_message(self, event):
        """Receive message from group and forward to WebSocket."""
        await self.send(text_data=json.dumps(event['message']))

    @database_sync_to_async
    def save_chat_message(self, data):
        """Save message in DB, decode base64 attachment if provided."""
        chat = Chat(
            category_id=data['category_id'],
            category_name=data['category_name'],
            sender_id=data['sender_id'],
            receiver_id=data['receiver_id'],
            message=data['message'],
            status='0'
        )

        attachment_b64 = data.get('attachment')
        if attachment_b64:
            try:
                # Validate base64 data
                base64.b64decode(attachment_b64, validate=True)
                chat.attachment = attachment_b64
            except Exception as e:
                print(f"Attachment decoding failed: {e}")
                # Optional: Raise error or ignore invalid attachment
                raise

        chat.save()
        return chat

    @database_sync_to_async
    def get_user_from_token(self, scope):
        """Extract and validate token from headers in scope."""
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

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from api.models import Notification
# after connect send all notifications to the user


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            await self.close()
        else:
            self.group_name = f"user_{user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            await self.send_all_notifications(user)
    
    async def send_all_notifications(self, user):
        notifications = await self.get_user_notifications(user)
        await self.send(text_data=json.dumps({
            "type": "all_notifications",
            "notifications": notifications
        }))
    
    async def get_user_notifications(self, user):
        notifications = Notification.objects.filter(user=user)
        return notifications
    
    async def disconnect(self, close_code):
        user = self.scope["user"]
        if not user.is_anonymous:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        # No-op for now
        pass

    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event["content"])) 
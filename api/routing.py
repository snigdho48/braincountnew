from django.urls import re_path
from . import consumers
from django.urls import path
from api.services.notification import NotificationApiView

urlpatterns2 = [
    path('notifications/', NotificationApiView.as_view(), name='notifications'),
] 
websocket_urlpatterns = [
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
] 


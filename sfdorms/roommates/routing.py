from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/call/(?p<room_name>\w+)/$', consumers.CallConsumer.as_asgi()),
]
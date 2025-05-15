# websocket_app/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # 定义 WebSocket 的 URL 路由
    # r'^ws/chat/(?P<room_name>\w+)/$' 是一个正则表达式，匹配类似 ws://<host>/ws/chat/<room_name>/
    # consumers.ChatConsumer 是处理这个 WebSocket 连接的消费者
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]
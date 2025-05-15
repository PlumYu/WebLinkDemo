# websocket_app/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    # 当 WebSocket 连接建立时调用
    async def connect(self):
        # 从 URL 路由参数中获取房间名
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        # 根据房间名构造一个 Channels 组名
        # Channels 组是一种广播机制，允许向组内的所有连接发送消息
        self.room_group_name = f'chat_{self.room_name}'

        # 将当前连接加入到组中
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # 接受 WebSocket 连接
        await self.accept()
        print(f"WebSocket 连接已建立: {self.channel_name} 加入房间 {self.room_name}")

    # 当 WebSocket 连接断开时调用
    async def disconnect(self, close_code):
        # 将当前连接从组中移除
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"WebSocket 连接已断开: {self.channel_name} 离开房间 {self.room_name}")

    # 当从 WebSocket 接收到消息时调用
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user = text_data_json.get('user', '匿名用户') # 获取用户名，默认为匿名用户

        print(f"从 {self.channel_name} 收到消息: {message} (来自: {user})")

        # 将接收到的消息广播到组内的所有连接
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message', # 指定处理该消息的方法名
                'message': message,
                'user': user
            }
        )

    # 从组接收到消息后调用的处理方法 (由 'type': 'chat_message' 触发)
    async def chat_message(self, event):
        message = event['message']
        user = event['user']

        # 将消息发送回 WebSocket 客户端
        await self.send(text_data=json.dumps({
            'message': message,
            'user': user
        }))
        print(f"向 {self.channel_name} 发送消息: {message} (来自: {user})")
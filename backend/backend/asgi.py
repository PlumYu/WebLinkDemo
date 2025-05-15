# backend/backend/asgi.py
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import websocket_app.routing # 导入 websocket_app 的路由配置

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Django 的 ASGI 应用
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    # Django 的常规 HTTP 请求由 get_asgi_application() 处理
    "http": django_asgi_app,
    # WebSocket 请求由 AuthMiddlewareStack 包裹的 URLRouter 处理
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_app.routing.websocket_urlpatterns
        )
    ),
})
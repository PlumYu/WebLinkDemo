# backend/backend/urls.py
from django.contrib import admin
from django.urls import path, include # 导入 include

urlpatterns = [
    path('admin/', admin.site.urls),
    # 将 sse_app 的 URL 包含进来，sse 相关请求将由 sse_app.urls 处理
    path('sse/', include('sse_app.urls')), 
    # WebSocket 连接通常不通过 Django 的常规 URL 系统处理，而是通过 Channels 的路由
    # 因此 websocket_app 的 URL 不在这里定义，而是在 asgi.py 中通过其 routing.py 处理
]
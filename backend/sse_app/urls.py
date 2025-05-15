# sse_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 定义 SSE 事件流的 URL
    # 当客户端访问 /sse/stream/ 时，将由 views.sse_stream视图函数处理
    path('stream/', views.sse_stream, name='sse_stream'),
]
# WebLinkDemo

这是一个演示项目，展示了如何使用 WebSocket 和 Server-Sent Events (SSE) 进行实时双向通信和服务器推送更新。

## 技术栈

*   **前端:**
    *   Vue 3
    *   TypeScript
    *   Vite
*   **后端:**
    *   Django
    *   Django Channels (用于 WebSocket 和 SSE)
    *   SQLite (默认开发数据库)

## 项目结构

```
WebLinkDemo/
├── backend/         # Django 后端项目
│   ├── backend/     # Django 项目配置
│   ├── sse_app/     # Django 应用处理 SSE
│   ├── websocket_app/ # Django 应用处理 WebSocket
│   ├── manage.py
│   └── requirements.txt
├── frontend/        # Vue 3 前端项目
│   ├── public/
│   ├── src/
│   │   ├── components/ # Vue 组件 (包括 SSEDemo.vue 和 WebSocketDemo.vue)
│   │   ├── App.vue
│   │   └── main.ts
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
└── README.md        # 本文件
```

## 安装与启动

### 后端 (Django)

1.  **进入后端目录:**
    ```bash
    cd backend
    ```

2.  **创建并激活虚拟环境 (推荐):**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    # source venv/bin/activate
    ```

3.  **安装依赖:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **数据库迁移:**
    ```bash
    python manage.py migrate
    ```

5.  **启动开发服务器 (默认运行在 `http://127.0.0.1:8001` 或 `http://0.0.0.0:8001`):**
    ```bash
    python manage.py runserver 0.0.0.0:8001 or uvicorn backend.asgi:application --host 0.0.0.0 --port 8001 --reload
    ```
    *注意: `SSEDemo.vue` 组件中连接的 SSE 地址是 `http://192.168.11.217:8001`，请确保后端服务在该地址可访问，或者相应修改前端代码中的 URL。*

### 前端 (Vue 3)

1.  **进入前端目录:**
    ```bash
    cd frontend
    ```

2.  **安装依赖:**
    ```bash
    npm install
    ```

3.  **启动开发服务器 (通常运行在 `http://localhost:5173`):**
    ```bash
    npm run dev
    ```

## 功能特性

*   **WebSocket 通信:**
    *   前端通过 WebSocket 连接到后端。
    *   可以发送消息到后端，并接收后端广播或推送的消息。
    *   演示了基本的双向实时通信。
*   **Server-Sent Events (SSE):**
    *   前端通过 SSE 连接到后端 `/taskStatus` 端点。
    *   后端可以向客户端单向推送任务状态更新。
    *   前端实时显示接收到的任务更新列表。

## 注意事项

*   确保后端服务先于前端启动，特别是如果前端组件在创建时就需要连接后端服务。
*   根据您的网络配置，可能需要调整前端代码中连接后端 API (WebSocket, SSE, HTTP) 的 URL 和端口。

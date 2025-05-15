<!-- frontend/src/components/WebSocketDemo.vue -->
<template>
  <div class="websocket-demo-container">
    <h2>WebSocket 聊天室 (房间: {{ roomName }})</h2>
    <div class="controls">
      <input v-model="roomNameInput" placeholder="输入房间名" :disabled="isConnected" />
      <input v-model="userNameInput" placeholder="输入你的名字" :disabled="isConnected" />
      <button @click="connectWebSocket" :disabled="isConnected || !roomNameInput.trim() || !userNameInput.trim()">
        连接
      </button>
      <button @click="disconnectWebSocket" :disabled="!isConnected">断开连接</button>
    </div>

    <div v-if="isConnected" class="chat-area">
      <div class="messages" ref="messagesContainer">
        <div v-for="(msg, index) in messages" :key="index" class="message"
             :class="{ 'my-message': msg.user === userName, 'other-message': msg.user !== userName }">
          <span class="user">{{ msg.user }}:</span> {{ msg.message }}
        </div>
      </div>
      <div class="input-area">
        <input v-model="newMessage" @keyup.enter="sendMessage" placeholder="输入消息..." />
        <button @click="sendMessage" :disabled="!newMessage.trim()">发送</button>
      </div>
    </div>
    <div v-if="connectionStatus" class="status-message">{{ connectionStatus }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onUnmounted } from 'vue';

// 响应式变量
const roomNameInput = ref<string>('default'); // 默认房间名输入
const userNameInput = ref<string>('用户' + Math.floor(Math.random() * 1000)); // 默认用户名输入
const roomName = ref<string>(''); // 当前连接的房间名
const userName = ref<string>(''); // 当前连接的用户名
const newMessage = ref<string>(''); // 新消息输入
const messages = ref<{ user: string; message: string }[]>([]); // 消息列表
const isConnected = ref<boolean>(false); // WebSocket 连接状态
const connectionStatus = ref<string>(''); // 连接状态消息
const messagesContainer = ref<HTMLElement | null>(null); // 消息容器的引用，用于自动滚动

let socket: WebSocket | null = null; // WebSocket 实例

// 连接 WebSocket
const connectWebSocket = () => {
  if (!roomNameInput.value.trim() || !userNameInput.value.trim()) {
    connectionStatus.value = '请输入房间名和你的名字。';
    return;
  }
  roomName.value = roomNameInput.value.trim();
  userName.value = userNameInput.value.trim();

  // 根据 vite.config.js 中的代理配置，这里的路径会自动代理到 ws://127.0.0.1:8000/ws/chat/<roomName>/
  // 注意：浏览器环境下的 WebSocket URL 需要以 ws:// 或 wss:// 开头
  // Vite 开发服务器会自动处理协议转换，但在生产环境中直接连接后端时需要确保协议正确
  const socketURL = `ws://${window.location.host}/ws/chat/${roomName.value}/`;
  
  connectionStatus.value = `正在连接到 ${socketURL}...`;
  console.log(`尝试连接 WebSocket: ${socketURL}`);

  socket = new WebSocket(socketURL);

  // 连接成功时
  socket.onopen = () => {
    isConnected.value = true;
    connectionStatus.value = `已连接到房间: ${roomName.value}`;
    messages.value.push({ user: '系统', message: `欢迎 ${userName.value} 加入房间 ${roomName.value}!` });
    console.log('WebSocket 连接已建立');
  };

  // 收到消息时
  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data as string);
      messages.value.push({ user: data.user, message: data.message });
      // 消息列表自动滚动到底部
      nextTick(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
        }
      });
      console.log('收到消息:', data);
    } catch (error) {
      console.error('处理接收到的消息时出错:', error, '原始数据:', event.data);
      messages.value.push({ user: '系统', message: `收到无法解析的数据: ${event.data}` });
    }
  };

  // 连接关闭时
  socket.onclose = (event) => {
    isConnected.value = false;
    connectionStatus.value = 'WebSocket 连接已断开。';
    if (event.wasClean) {
      console.log(`WebSocket 连接正常关闭, code=${event.code}, reason=${event.reason}`);
    } else {
      console.error('WebSocket 连接意外断开');
      connectionStatus.value += ' (连接意外断开)';
    }
    socket = null;
  };

  // 连接出错时
  socket.onerror = (error) => {
    isConnected.value = false;
    connectionStatus.value = 'WebSocket 连接失败。请检查控制台获取更多信息。';
    console.error('WebSocket 错误:', error);
    socket = null; // 清理 socket 实例
  };
};

// 发送消息
const sendMessage = () => {
  if (socket && socket.readyState === WebSocket.OPEN && newMessage.value.trim()) {
    const messageData = {
      message: newMessage.value.trim(),
      user: userName.value,
    };
    socket.send(JSON.stringify(messageData));
    console.log('发送消息:', messageData);
    newMessage.value = ''; // 清空输入框
  } else {
    connectionStatus.value = '无法发送消息，WebSocket 未连接或消息为空。';
    console.warn('尝试发送消息失败，WebSocket 未连接或消息为空。');
  }
};

// 断开 WebSocket 连接
const disconnectWebSocket = () => {
  if (socket) {
    socket.close();
    console.log('手动断开 WebSocket 连接');
  }
  // onclose 事件处理器会自动更新状态
};

// 组件卸载时，确保关闭 WebSocket 连接
onUnmounted(() => {
  if (socket) {
    socket.close();
    console.log('组件卸载，关闭 WebSocket 连接');
  }
});

</script>

<style scoped>
.websocket-demo-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 15px;
  border: 1px solid #42b983;
  border-radius: 5px;
  background-color: #f0f9f4;
}

.controls {
  margin-bottom: 15px;
  display: flex;
  gap: 10px;
  align-items: center;
}

.controls input {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.controls button {
  padding: 8px 12px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.controls button:disabled {
  background-color: #a5d6a7;
  cursor: not-allowed;
}

.controls button:hover:not(:disabled) {
  background-color: #36a46f;
}

.chat-area {
  width: 100%;
  max-width: 500px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #fff;
}

.messages {
  height: 200px;
  overflow-y: auto;
  padding: 10px;
  border-bottom: 1px solid #ddd;
  display: flex;
  flex-direction: column;
}

.message {
  margin-bottom: 8px;
  padding: 6px 10px;
  border-radius: 15px;
  max-width: 70%;
  word-wrap: break-word;
}

.my-message {
  background-color: #dcf8c6; /* 类似微信的绿色气泡 */
  align-self: flex-end;
  text-align: right;
}

.other-message {
  background-color: #f0f0f0; /* 灰色气泡 */
  align-self: flex-start;
  text-align: left;
}

.message .user {
  font-weight: bold;
  margin-right: 5px;
  color: #555;
}

.input-area {
  display: flex;
  padding: 10px;
}

.input-area input {
  flex-grow: 1;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin-right: 10px;
}

.input-area button {
  padding: 8px 12px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.input-area button:disabled {
  background-color: #a5d6a7;
}

.status-message {
  margin-top: 10px;
  color: #777;
  font-style: italic;
}
</style>
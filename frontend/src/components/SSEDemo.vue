<template>
  <div class="sse-demo-container">
    <h2>SSE (Server-Sent Events) 实时更新 (新版)</h2>
    <div class="controls">
      <button
        @click="startSSE"
        :disabled="isReceiving || isLoadingSSE"
      >
        {{ isLoadingSSE ? '连接中...' : '开始接收事件' }}
      </button>
      <button
        @click="stopSSE"
        :disabled="!isReceiving && !isLoadingSSE"
      >停止接收事件</button>
    </div>
    <div
      class="status-message"
      :class="{ 'error': sseStatus.isError }"
    >{{ sseStatus.text }}</div>
    <div
      v-if="events.length > 0"
      class="events-log"
    >
      <h3>接收到的事件 (最新 {{ MAX_EVENTS_DISPLAY }} 条):</h3>
      <ul>
        <li
          v-for="eventItem in events"
          :key="eventItem.uniqueKey"
        >
          ID: {{ eventItem.payload.id }}, 
          消息: {{ eventItem.payload.message }}, 
          时间: {{ formatTimestamp(eventItem.payload.timestamp * 1000) }}
          <span class="raw-event-id">(Raw SSE ID: {{ eventItem.rawSSEEventId || 'None' }})</span>
        </li>
      </ul>
    </div>
    <div
      v-if="events.length === 0 && isReceiving"
      class="status-message"
    >
      已连接，等待服务器发送事件...
    </div>
    <div
      v-if="lastRawData"
      class="raw-event-display"
    >
      <h4>最新原始数据 (event.data):</h4>
      <pre>{{ lastRawData }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted, shallowRef } from "vue";

// 后端 SSE 事件的载荷结构 (根据 backend/sse_app/views.py)
interface BackendSSEEventPayload {
  id: number;
  message: string;
  timestamp: number; // Unix timestamp in seconds
}

// 前端用于在列表中显示的事件结构
interface FrontendDisplayEvent {
  uniqueKey: string; // 前端生成的唯一key
  payload: BackendSSEEventPayload; // 单个事件的载荷
  rawSSEEventId?: string | null; // 原始 SSE 事件的 ID (如果后端发送了 `id: ...`)
}

interface StatusMessage {
  text: string;
  isError: boolean;
}

const MAX_EVENTS_DISPLAY = 20; // 可以适当增加，因为现在每个任务更新是一个条目

const events = ref<FrontendDisplayEvent[]>([]);
const isReceiving = ref<boolean>(false);
const isLoadingSSE = ref<boolean>(false);
const sseStatus = ref<StatusMessage>({ text: "尚未连接 SSE", isError: false });
const lastRawData = ref<string>("");

const eventSource = shallowRef<EventSource | null>(null);

const startSSE = () => {
  if (eventSource.value || isLoadingSSE.value) {
    sseStatus.value = { text: "已在接收或正在尝试连接。", isError: false };
    return;
  }

  isLoadingSSE.value = true;

  // Vite 开发服务器会将 /sse 代理到后端 http://127.0.0.1:8000/sse
  // 后端 sse_app/urls.py 定义了 stream/ 路径
  // 所以完整路径是 /sse/stream/
  const finalUrl = "/sse/stream/"; // 使用相对路径，让 Vite 代理处理

  console.log("Generated URL for backend SSE stream:", finalUrl);
  sseStatus.value = { text: `正在连接到 SSE 源: ${finalUrl}`, isError: false };
  console.log(`[FRONTEND] Attempting to connect to SSE: ${finalUrl}`);

  try {
    eventSource.value = new EventSource(finalUrl);

    eventSource.value.onopen = () => {
      isLoadingSSE.value = false;
      isReceiving.value = true;
      sseStatus.value = {
        text: "已连接到 SSE 源，等待事件...",
        isError: false,
      };
      console.log("[FRONTEND] SSE connection established.");
    };

    // 监听名为 'message' (或你后端指定的事件名, 如果没有指定就是 'message')
    eventSource.value.addEventListener("message", (event: MessageEvent) => { // <--- 修改这里
  isLoadingSSE.value = false;
  isReceiving.value = true;
  lastRawData.value = event.data;

  console.log("[FRONTEND] SSE event received (type: message):"); // 确认事件类型
  console.log("  Raw event.data:", event.data);
  console.log("  Raw event.lastEventId:", event.lastEventId); // 这个是 SSE 规范中的 id: xxx

  try {
    // 解析得到的是一个 BackendSSEEventPayload 对象
    const singleEventPayload: BackendSSEEventPayload = JSON.parse(event.data);

    // 你不再需要检查是否为数组或遍历数组了

    // 确保解析后的对象是你期望的结构
    if (!singleEventPayload || typeof singleEventPayload.id === 'undefined') {
      console.warn("[FRONTEND] Received an invalid event payload structure:", singleEventPayload);
      // 可以选择在这里添加一个错误提示到 UI
      const errorEvent: FrontendDisplayEvent = {
        uniqueKey: `err-payload-${Date.now()}`,
        payload: { id: -1, message: "Invalid payload structure received", timestamp: Math.floor(Date.now()/1000) },
        rawSSEEventId: event.lastEventId,
      };
      events.value.unshift(errorEvent);
      if (events.value.length > MAX_EVENTS_DISPLAY) {
        events.value.pop();
      }
      sseStatus.value = { text: "收到无效结构的事件数据", isError: true };
      return;
    }

    // 创建用于显示的对象，使用 FrontendDisplayEvent 接口
    const newDisplayEvent: FrontendDisplayEvent = {
      uniqueKey: `event-${singleEventPayload.id}-${Date.now()}-${Math.random()}`, // 确保 key 唯一性
      payload: singleEventPayload, // 直接使用解析后的单个对象
      rawSSEEventId: event.lastEventId, // 这是 SSE 规范中的 id
    };

    events.value.unshift(newDisplayEvent);

    if (events.value.length > MAX_EVENTS_DISPLAY) {
      // 移除多余的旧事件
      events.value.splice(
        MAX_EVENTS_DISPLAY,
        events.value.length - MAX_EVENTS_DISPLAY
      );
    }

    sseStatus.value = { text: `收到事件 ID: ${singleEventPayload.id}, 消息: ${singleEventPayload.message.substring(0,30)}...`, isError: false };

  } catch (error) {
    console.error(
      "[FRONTEND] Failed to parse SSE event.data or process event:",
      error,
      "Raw data:",
      event.data
    );
    // 当解析失败时，可以记录一条通用错误
    const fallbackEvent: FrontendDisplayEvent = { // 使用 FrontendDisplayEvent
      uniqueKey: `err-${Date.now()}`,
      payload: { // 提供一个符合 BackendSSEEventPayload 结构的 fallback 对象
        id: -1, // 表示错误或未知
        message: `[UNPARSABLE DATA]: ${event.data.substring(0, 100)}...`,
        timestamp: Math.floor(Date.now() / 1000), // 当前时间戳
      },
      rawSSEEventId: event.lastEventId,
    };
    events.value.unshift(fallbackEvent);
    if (events.value.length > MAX_EVENTS_DISPLAY) {
      events.value.pop();
    }

    sseStatus.value = {
      text: `解析数据失败，已记录原始数据.`,
      isError: true,
    };
  }
});

    eventSource.value.onerror = (errorEvent) => {
      // onError 逻辑保持不变
      isLoadingSSE.value = false;
      isReceiving.value = false;
      const readyState = eventSource.value?.readyState;
      let statusText = "SSE 连接错误或流已关闭。";
      if (readyState === EventSource.CLOSED) {
        statusText += " (连接已关闭)";
      } else if (readyState === EventSource.CONNECTING) {
        statusText += " (仍在尝试连接)";
      }
      sseStatus.value = {
        text: statusText + " 检查浏览器网络面板和后端/代理日志。",
        isError: true,
      };
      console.error(
        "[FRONTEND] SSE EventSource error event:",
        errorEvent,
        "ReadyState:",
        readyState
      );
      if (eventSource.value) {
        eventSource.value.close();
        eventSource.value = null;
      }
    };
  } catch (e) {
    // 创建 EventSource 实例失败的逻辑保持不变
    isLoadingSSE.value = false;
    console.error("[FRONTEND] Failed to create EventSource instance:", e);
    sseStatus.value = {
      text: `创建 SSE 连接失败: ${(e as Error).message}`,
      isError: true,
    };
    if (eventSource.value) {
      eventSource.value.close();
      eventSource.value = null;
    }
  }
};

const stopSSE = () => {
  // stopSSE 逻辑保持不变
  if (eventSource.value) {
    eventSource.value.close();
    console.log("[FRONTEND] Manually closed SSE connection.");
  }
  eventSource.value = null;
  isReceiving.value = false;
  isLoadingSSE.value = false;
  sseStatus.value = { text: "SSE 连接已关闭。", isError: false };
};

const formatTimestamp = (msTimestamp: number): string => {
  // formatTimestamp 逻辑保持不变
  // 不过你的后端数据示例中没有 timestamp，如果实际有，再用它
  // 你后端的示例数据是：{'task_id': '...', 'status': '...', ...}
  // 如果你的 TaskStatusPayload 中也有 timestamp (秒级)，那么这里需要乘以 1000
  if (isNaN(msTimestamp)) return "N/A";
  return new Date(msTimestamp).toLocaleTimeString([], {
    // 假设 msTimestamp 已经是毫秒
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
};

onUnmounted(() => {
  stopSSE();
});
</script>

<style scoped>
.sse-demo-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 15px;
  border: 1px solid #ffc107; /* 橙色边框，与 WebSocket 区分 */
  border-radius: 5px;
  background-color: #fff8e1;
}

.controls {
  margin-bottom: 15px;
  display: flex;
  gap: 10px;
}

.controls button {
  padding: 8px 12px;
  background-color: #ff9800; /* 橙色按钮 */
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.controls button:disabled {
  background-color: #ffcc80;
  cursor: not-allowed;
}

.controls button:hover:not(:disabled) {
  background-color: #f57c00;
}

.status-message {
  margin-bottom: 10px;
  color: #777;
  font-style: italic;
}

.events-log {
  width: 100%;
  max-width: 500px;
  text-align: left;
  background-color: #fff;
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 4px;
  max-height: 200px;
  overflow-y: auto;
}

.events-log h3 {
  margin-top: 0;
  color: #333;
}

.events-log ul {
  list-style-type: none;
  padding-left: 0;
}

.events-log li {
  padding: 5px 0;
  border-bottom: 1px dashed #eee;
  font-size: 0.9em;
}

.events-log li:last-child {
  border-bottom: none;
}

.raw-event-display {
  margin-top: 15px;
  width: 100%;
  max-width: 500px;
  text-align: left;
}

.raw-event-display h4 {
  margin-bottom: 5px;
  color: #555;
}

.raw-event-display pre {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  white-space: pre-wrap; /* 允许换行 */
  word-break: break-all; /* 强制换行 */
  font-size: 0.85em;
  max-height: 100px;
  overflow-y: auto;
}
</style>
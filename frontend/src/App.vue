<!-- frontend/src/App.vue -->
<template>
  <div id="app-container">
    <h1>Vue 3 WebSocket 和 SSE 示例</h1>
    <div class="demo-section">
      <WebSocketDemo />
    </div>
    <div class="demo-section">
      <SSEDemo />
    </div>
  </div>
</template>

<script setup lang="ts">
// 导入 WebSocket 和 SSE 示例组件
import WebSocketDemo from "./components/WebSocketDemo.vue";
import SSEDemo from "./components/SSEDemo.vue";
// TypeScript setup script
// 这里不需要额外的逻辑，因为组件的导入和使用已在模板中声明
</script>

<style scoped>
#app-container {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.demo-section {
  border: 1px solid #ccc;
  padding: 20px;
  margin: 20px;
  border-radius: 8px;
  width: 80%;
  max-width: 600px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

h1 {
  color: #42b983;
}
</style>
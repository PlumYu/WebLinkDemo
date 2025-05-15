// frontend/src/main.ts
import { createApp } from 'vue' // 导入 createApp 用于创建 Vue 应用实例
import './style.css' // 导入全局样式 (如果需要的话，暂时留空)
import App from './App.vue' // 导入根组件 App

// 创建 Vue 应用实例并挂载到 #app 元素上
createApp(App).mount('#app')
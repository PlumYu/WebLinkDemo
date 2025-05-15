import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [vue()],
    server: {
        // 配置代理以允许前端访问后端 API，避免CORS问题
        proxy: {
            // WebSocket 代理
            '/ws': {
                target: 'ws://127.0.0.1:8000', // 后端 WebSocket 服务器地址
                ws: true, // 开启 WebSocket 代理
                changeOrigin: true,
            },
            // SSE 和其他 API 代理
            '/sse': {
                target: 'http://0.0.0.0:8001', // 后端 SSE/API 服务器地址 (移除末尾斜杠)
                changeOrigin: true,
                // rewrite: (path) => path.replace(new RegExp("^/sse"), ''), // 保持注释，因为后端URL结构是 /sse/stream/
                // 如果你的 SSE 端点在 /api/sse 下，可以这样配置
                // rewrite: (path) => path.replace(/^\/api/, '') 
                configure: (proxy, options) => {
                    proxy.on('proxyRes', (proxyRes, req, res) => {
                        console.log('[VITE PROXY /sse] Received headers from target:', proxyRes.headers);
                    });
                    proxy.on('error', (err, req, res) => {
                        console.error('[VITE PROXY /sse] Proxy error:', err);
                    });
                }
            },
            // 如果还有其他 API 端点，也可以在这里配置
            // '/api': {
            //   target: 'http://127.0.0.1:8000',
            //   changeOrigin: true,
            //   rewrite: (path) => path.replace(/^\/api/, '') 
            // }
        }
    }
})
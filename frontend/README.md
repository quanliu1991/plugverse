# PlugVerse 前端开发指南

## 技术栈

- **框架:** Vue 3.4 + TypeScript
- **构建工具:** Vite 5
- **UI 组件库:** Element Plus 2.5
- **路由:** Vue Router 4
- **状态管理:** Pinia 2
- **HTTP 客户端:** Axios

## 项目结构

```
frontend/
├── src/
│   ├── main.ts              # 应用入口
│   ├── App.vue              # 根组件
│   ├── api/                 # API 接口
│   │   └── index.ts
│   ├── components/          # 公共组件
│   │   ├── Sidebar.vue
│   │   └── Header.vue
│   ├── router/              # 路由配置
│   │   └── index.ts
│   ├── stores/              # Pinia 状态管理
│   │   └── pluginStore.ts
│   ├── views/               # 页面组件
│   │   ├── HomeView.vue
│   │   ├── PluginsView.vue
│   │   ├── TasksView.vue
│   │   ├── FilesView.vue
│   │   ├── TranscribeView.vue
│   │   └── SettingsView.vue
│   └── assets/              # 静态资源
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## 开发命令

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

## 页面路由

| 路径 | 组件 | 说明 |
|------|------|------|
| `/` | HomeView | 首页仪表盘 |
| `/plugins` | PluginsView | 插件管理 |
| `/tasks` | TasksView | 任务管理 |
| `/files` | FilesView | 文件管理 |
| `/transcribe` | TranscribeView | 音视频转写 |
| `/settings` | SettingsView | 系统设置 |

## API 对接

后端 API 地址：`http://localhost:8000/api`

开发代理已配置在 `vite.config.ts`，前端请求 `/api` 会自动代理到后端。

### 主要 API

```typescript
// 插件管理
GET  /api/plugins          # 获取插件列表
POST /api/plugins/:id/enable   # 启用插件
POST /api/plugins/:id/disable  # 禁用插件

// 任务管理
GET  /api/tasks            # 获取任务列表
POST /api/tasks            # 创建任务
GET  /api/tasks/:id/result # 获取任务结果

// 文件管理
POST /api/files/upload     # 上传文件
GET  /api/files/:id/download # 下载文件
```

## 状态管理

使用 Pinia 管理全局状态：

```typescript
import { usePluginStore } from '@/stores/pluginStore'

const pluginStore = usePluginStore()
await pluginStore.loadPlugins()
```

## 开发规范

1. **组件命名:** PascalCase (如 `PluginsView.vue`)
2. **脚本语言:** 使用 `<script setup lang="ts">`
3. **类型定义:** 使用 TypeScript 接口定义数据结构
4. **样式作用域:** 所有组件使用 `scoped`
5. **图标:** 使用 Element Plus Icons

## 下一步

- [ ] 连接真实后端 API
- [ ] 实现 WebSocket 实时通信
- [ ] 添加加载状态和错误处理
- [ ] 响应式设计优化
- [ ] 单元测试

---

**更新时间:** 2026-03-30

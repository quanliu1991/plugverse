<template>
  <div class="plugins-view">
    <div class="page-header">
      <h1>插件管理</h1>
      <el-button type="primary" @click="handleInstall">
        <el-icon><Download /></el-icon>
        安装插件
      </el-button>
    </div>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="8" v-for="plugin in plugins" :key="plugin.id">
        <el-card shadow="hover" class="plugin-card">
          <template #header>
            <div class="plugin-header">
              <span class="plugin-icon">{{ plugin.icon }}</span>
              <div class="plugin-info">
                <h3>{{ plugin.name }}</h3>
                <span class="plugin-version">v{{ plugin.version }}</span>
              </div>
              <el-switch
                v-model="plugin.active"
                active-color="#13ce66"
                inactive-color="#ff4949"
                @change="handleToggle(plugin)"
              />
            </div>
          </template>
          <div class="plugin-body">
            <p class="plugin-desc">{{ plugin.description }}</p>
            <el-tag size="small" :type="getTypeTag(plugin.type)">{{ plugin.type }}</el-tag>
            <div class="plugin-actions">
              <el-button size="small" @click="handleConfigure(plugin)">配置</el-button>
              <el-button size="small" type="danger" @click="handleUninstall(plugin)">卸载</el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Download } from '@element-plus/icons-vue'

const plugins = ref([
  {
    id: 'hello-world',
    name: 'Hello World',
    version: '1.0.0',
    icon: '👋',
    description: '一个简单的示例插件，用于演示插件开发基础',
    type: '示例',
    active: true
  },
  {
    id: 'media-transcribe',
    name: '音视频转文字',
    version: '1.0.0',
    icon: '🎤',
    description: '使用 Faster-Whisper 进行音视频转文字，支持多种格式输出',
    type: '媒体处理',
    active: true
  }
])

const getTypeTag = (type: string) => {
  const map: Record<string, any> = {
    '示例': 'info',
    '媒体处理': 'primary',
    '图片处理': 'success',
    '数据导出': 'warning',
    'AI 助手': 'danger'
  }
  return map[type] || 'info'
}

const handleInstall = () => {
  console.log('Install plugin')
}

const handleToggle = (plugin: any) => {
  console.log('Toggle plugin:', plugin.name, plugin.active)
}

const handleConfigure = (plugin: any) => {
  console.log('Configure plugin:', plugin.name)
}

const handleUninstall = (plugin: any) => {
  console.log('Uninstall plugin:', plugin.name)
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.plugin-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.plugin-icon {
  font-size: 32px;
}

.plugin-info {
  flex: 1;
}

.plugin-info h3 {
  margin: 0 0 4px 0;
  font-size: 16px;
}

.plugin-version {
  font-size: 12px;
  color: #909399;
}

.plugin-desc {
  color: #606266;
  font-size: 14px;
  margin-bottom: 12px;
  line-height: 1.5;
}

.plugin-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}
</style>

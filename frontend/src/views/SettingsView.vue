<template>
  <div class="settings-view">
    <h1>系统设置</h1>
    
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>🎨 外观设置</span>
          </template>
          <el-form label-width="100px">
            <el-form-item label="主题模式">
              <el-radio-group v-model="settings.theme">
                <el-radio-button label="light">浅色</el-radio-button>
                <el-radio-button label="dark">深色</el-radio-button>
                <el-radio-button label="auto">自动</el-radio-button>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="语言">
              <el-select v-model="settings.language" style="width: 150px">
                <el-option label="简体中文" value="zh-CN" />
                <el-option label="English" value="en" />
              </el-select>
            </el-form-item>
          </el-form>
        </el-card>
        
        <el-card style="margin-top: 20px">
          <template #header>
            <span>💾 存储设置</span>
          </template>
          <el-form label-width="100px">
            <el-form-item label="存储路径">
              <el-input v-model="settings.storagePath" placeholder="/data/plugverse/storage" />
            </el-form-item>
            <el-form-item label="最大存储">
              <el-input v-model="settings.maxStorage" placeholder="10GB" />
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>⚙️ 系统信息</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="版本号">v0.2.0</el-descriptions-item>
            <el-descriptions-item label="构建日期">2026-03-30</el-descriptions-item>
            <el-descriptions-item label="后端状态">
              <el-tag type="success">运行中</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="API 地址">http://localhost:8000</el-descriptions-item>
            <el-descriptions-item label="已安装插件">2</el-descriptions-item>
            <el-descriptions-item label="总任务数">1</el-descriptions-item>
          </el-descriptions>
        </el-card>
        
        <el-card style="margin-top: 20px">
          <template #header>
            <span>🔧 操作</span>
          </template>
          <el-button type="warning" @click="handleRestart">重启服务</el-button>
          <el-button type="danger" @click="handleReset">重置配置</el-button>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const settings = ref({
  theme: 'light',
  language: 'zh-CN',
  storagePath: '/data/plugverse/storage',
  maxStorage: '10GB'
})

const handleRestart = () => {
  console.log('Restart service')
}

const handleReset = () => {
  console.log('Reset config')
}
</script>

<style scoped>
.settings-view h1 {
  margin-bottom: 10px;
}
</style>

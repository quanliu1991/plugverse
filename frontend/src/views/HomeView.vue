<template>
  <div class="home">
    <h1>欢迎使用 PlugVerse 插件化平台</h1>
    
    <el-row :gutter="20" style="margin-top: 30px">
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>🧩 已安装插件</span>
            </div>
          </template>
          <div class="card-value">2</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>📊 运行中任务</span>
            </div>
          </template>
          <div class="card-value">0</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>📁 存储文件</span>
            </div>
          </template>
          <div class="card-value">0</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>⚙️ 系统状态</span>
            </div>
          </template>
          <div class="card-value"><el-tag type="success">正常</el-tag></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top: 30px">
      <template #header>
        <div class="card-header">
          <span>📈 项目进度</span>
        </div>
      </template>
      <div class="progress-info">
        <el-progress :percentage="60" :format="() => '总进度 60% (44/73 任务)'" />
        <el-descriptions :column="3" style="margin-top: 20px">
          <el-descriptions-item label="Phase 1">✅ 100%</el-descriptions-item>
          <el-descriptions-item label="Phase 2">✅ 100%</el-descriptions-item>
          <el-descriptions-item label="Phase 3">🔄 5%</el-descriptions-item>
          <el-descriptions-item label="Phase 4">⬜ 0%</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>

    <el-card style="margin-top: 30px">
      <template #header>
        <div class="card-header">
          <span>🔌 已安装插件</span>
        </div>
      </template>
      <el-table :data="plugins" style="width: 100%">
        <el-table-column prop="name" label="插件名称" />
        <el-table-column prop="version" label="版本" width="100" />
        <el-table-column prop="type" label="类型" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'active' ? 'success' : 'info'">
              {{ scope.row.status === 'active' ? '已启用' : '已禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button size="small" @click="handleConfigure(scope.row)">配置</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const plugins = ref([
  { name: 'Hello World', version: '1.0.0', type: '示例', status: 'active' },
  { name: '音视频转文字', version: '1.0.0', type: '媒体处理', status: 'active' }
])

const handleConfigure = (plugin: any) => {
  console.log('Configure plugin:', plugin)
}
</script>

<style scoped>
.home h1 {
  color: #303133;
  margin-bottom: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-value {
  font-size: 32px;
  font-weight: bold;
  color: #409EFF;
  text-align: center;
  padding: 20px 0;
}

.progress-info {
  padding: 10px 0;
}
</style>

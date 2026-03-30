<template>
  <div class="tasks-view">
    <div class="page-header">
      <h1>任务管理</h1>
      <el-button type="primary" @click="handleCreateTask">
        <el-icon><Plus /></el-icon>
        创建任务
      </el-button>
    </div>

    <el-card style="margin-top: 20px">
      <el-table :data="tasks" style="width: 100%">
        <el-table-column prop="id" label="任务 ID" width="120" />
        <el-table-column prop="name" label="任务名称" />
        <el-table-column prop="plugin" label="插件" width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusTag(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度" width="150">
          <template #default="scope">
            <el-progress :percentage="scope.row.progress" :status="scope.row.status === 'failed' ? 'exception' : undefined" />
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="handleViewResult(scope.row)">查看结果</el-button>
            <el-button size="small" type="danger" v-if="scope.row.status === 'running'" @click="handleCancel(scope.row)">取消</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Plus } from '@element-plus/icons-vue'

const tasks = ref([
  {
    id: 'task-001',
    name: '转写会议录音.mp3',
    plugin: '音视频转文字',
    status: 'completed',
    progress: 100,
    createdAt: '2026-03-30 07:30'
  }
])

const getStatusTag = (status: string) => {
  const map: Record<string, any> = {
    'pending': 'info',
    'running': 'warning',
    'completed': 'success',
    'failed': 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    'pending': '等待中',
    'running': '进行中',
    'completed': '已完成',
    'failed': '失败'
  }
  return map[status] || status
}

const handleCreateTask = () => {
  console.log('Create task')
}

const handleViewResult = (task: any) => {
  console.log('View result:', task)
}

const handleCancel = (task: any) => {
  console.log('Cancel task:', task)
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

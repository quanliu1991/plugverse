<template>
  <div class="files-view">
    <div class="page-header">
      <h1>文件管理</h1>
      <el-upload
        :auto-upload="true"
        :show-file-list="false"
        @change="handleUpload"
      >
        <el-button type="primary">
          <el-icon><Upload /></el-icon>
          上传文件
        </el-button>
      </el-upload>
    </div>

    <el-card style="margin-top: 20px">
      <el-table :data="files" style="width: 100%">
        <el-table-column prop="name" label="文件名">
          <template #default="scope">
            <el-icon><Document /></el-icon>
            <span style="margin-left: 8px">{{ scope.row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="size" label="大小" width="120" />
        <el-table-column prop="type" label="类型" width="100" />
        <el-table-column prop="uploadedAt" label="上传时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="handleDownload(scope.row)">下载</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Upload, Document } from '@element-plus/icons-vue'

const files = ref<any[]>([])

const handleUpload = (file: any) => {
  console.log('Upload file:', file.name)
  files.value.push({
    name: file.name,
    size: formatSize(file.size),
    type: file.name.split('.').pop(),
    uploadedAt: new Date().toLocaleString()
  })
}

const formatSize = (bytes: number) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / 1024 / 1024).toFixed(2) + ' MB'
}

const handleDownload = (file: any) => {
  console.log('Download:', file.name)
}

const handleDelete = (file: any) => {
  console.log('Delete:', file.name)
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

<template>
  <div class="header">
    <div class="breadcrumb">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item v-if="currentRoute">{{ currentRoute }}</el-breadcrumb-item>
      </el-breadcrumb>
    </div>
    <div class="user-info">
      <el-dropdown>
        <span class="user-name">
          <el-avatar :size="32" icon="UserFilled" />
          <span style="margin-left: 8px">Admin</span>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item>个人中心</el-dropdown-item>
            <el-dropdown-item divided>退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const currentRoute = computed(() => {
  const pathMap: Record<string, string> = {
    '/plugins': '插件管理',
    '/tasks': '任务管理',
    '/files': '文件管理',
    '/transcribe': '音视频转写',
    '/settings': '系统设置'
  }
  return pathMap[route.path] || ''
})
</script>

<style scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.user-name {
  display: flex;
  align-items: center;
  cursor: pointer;
}
</style>

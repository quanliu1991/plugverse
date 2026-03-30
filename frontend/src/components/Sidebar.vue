<template>
  <div class="sidebar">
    <div class="logo">
      <h2>🌌 PlugVerse</h2>
    </div>
    <el-menu
      :default-active="activeMenu"
      background-color="#304156"
      text-color="#bfcbd9"
      active-text-color="#409EFF"
      router
    >
      <el-menu-item index="/">
        <el-icon><HomeFilled /></el-icon>
        <span>首页</span>
      </el-menu-item>
      <el-menu-item index="/plugins">
        <el-icon><Grid /></el-icon>
        <span>插件管理</span>
      </el-menu-item>
      <el-menu-item index="/tasks">
        <el-icon><Document /></el-icon>
        <span>任务管理</span>
      </el-menu-item>
      <el-menu-item index="/files">
        <el-icon><Folder /></el-icon>
        <span>文件管理</span>
      </el-menu-item>
      <el-menu-item index="/transcribe">
        <el-icon><Microphone /></el-icon>
        <span>音视频转写</span>
      </el-menu-item>
      <el-menu-item index="/settings">
        <el-icon><Setting /></el-icon>
        <span>系统设置</span>
      </el-menu-item>
    </el-menu>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { HomeFilled, Grid, Document, Folder, Microphone, Setting } from '@element-plus/icons-vue'

const route = useRoute()
const activeMenu = computed(() => route.path as string)
</script>

<style scoped>
.sidebar {
  height: 100%;
}

.logo {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid #3d4a5a;
}

.logo h2 {
  margin: 0;
  font-size: 20px;
  color: #fff;
}

.el-menu {
  border-right: none;
}
</style>

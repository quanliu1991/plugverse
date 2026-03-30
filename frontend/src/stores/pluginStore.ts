import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { pluginsApi } from '@/api'

export interface Plugin {
  id: string
  name: string
  version: string
  description: string
  type: string
  status: 'active' | 'inactive' | 'error'
  icon?: string
}

export const usePluginStore = defineStore('plugins', () => {
  const plugins = ref<Plugin[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const activePlugins = computed(() => 
    plugins.value.filter(p => p.status === 'active')
  )

  async function loadPlugins() {
    loading.value = true
    try {
      const data = await pluginsApi.list()
      plugins.value = data.plugins || []
    } catch (e: any) {
      error.value = e.message
      // 使用模拟数据
      plugins.value = [
        { id: 'hello-world', name: 'Hello World', version: '1.0.0', description: '示例插件', type: '示例', status: 'active', icon: '👋' },
        { id: 'media-transcribe', name: '音视频转文字', version: '1.0.0', description: '音视频转文字', type: '媒体处理', status: 'active', icon: '🎤' }
      ]
    } finally {
      loading.value = false
    }
  }

  async function togglePlugin(id: string, enable: boolean) {
    try {
      if (enable) {
        await pluginsApi.enable(id)
      } else {
        await pluginsApi.disable(id)
      }
      const plugin = plugins.value.find(p => p.id === id)
      if (plugin) {
        plugin.status = enable ? 'active' : 'inactive'
      }
    } catch (e: any) {
      error.value = e.message
    }
  }

  return {
    plugins,
    loading,
    error,
    activePlugins,
    loadPlugins,
    togglePlugin
  }
})

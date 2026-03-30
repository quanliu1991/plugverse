<template>
  <div class="transcribe-view">
    <h1>音视频转文字</h1>
    
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>📤 上传文件</span>
          </template>
          <el-upload
            drag
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此处或 <em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 mp3/wav/m4a/flac/mp4/avi/mov 格式
              </div>
            </template>
          </el-upload>
          
          <el-form :model="config" label-width="100px" style="margin-top: 20px">
            <el-form-item label="模型大小">
              <el-select v-model="config.modelSize" style="width: 100%">
                <el-option label="Tiny (最快)" value="tiny" />
                <el-option label="Base (快)" value="base" />
                <el-option label="Small (平衡)" value="small" />
                <el-option label="Medium (慢)" value="medium" />
                <el-option label="Large (最慢)" value="large" />
              </el-select>
            </el-form-item>
            <el-form-item label="识别语言">
              <el-select v-model="config.language" style="width: 100%">
                <el-option label="自动检测" value="auto" />
                <el-option label="中文" value="zh" />
                <el-option label="英文" value="en" />
                <el-option label="日文" value="ja" />
              </el-select>
            </el-form-item>
            <el-form-item label="输出格式">
              <el-select v-model="config.outputFormat" style="width: 100%">
                <el-option label="TXT 文本" value="txt" />
                <el-option label="SRT 字幕" value="srt" />
                <el-option label="VTT 字幕" value="vtt" />
                <el-option label="JSON (带时间戳)" value="json" />
              </el-select>
            </el-form-item>
          </el-form>
          
          <el-button type="primary" style="width: 100%; margin-top: 20px" @click="handleStart" :disabled="!selectedFile">
            开始转写
          </el-button>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>📊 转写进度</span>
          </template>
          <div v-if="transcribing" style="text-align: center; padding: 40px 0">
            <el-progress type="circle" :percentage="progress" :status="progressStatus" />
            <p style="margin-top: 20px">{{ statusText }}</p>
          </div>
          <el-empty v-else description="暂无转写任务" />
        </el-card>
        
        <el-card style="margin-top: 20px">
          <template #header>
            <span>📝 转写结果</span>
          </template>
          <el-input
            v-model="result"
            type="textarea"
            :rows="10"
            placeholder="转写结果将显示在这里..."
            readonly
          />
          <div style="margin-top: 10px; display: flex; gap: 10px">
            <el-button @click="handleCopy">复制</el-button>
            <el-button type="primary" @click="handleExport">导出</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'

const selectedFile = ref<any>(null)
const config = ref({
  modelSize: 'small',
  language: 'auto',
  outputFormat: 'txt'
})
const transcribing = ref(false)
const progress = ref(0)
const progressStatus = ref<'success' | 'exception' | undefined>(undefined)
const statusText = ref('')
const result = ref('')

const handleFileChange = (file: any) => {
  selectedFile.value = file
}

const handleStart = async () => {
  if (!selectedFile.value) return
  
  transcribing.value = true
  progress.value = 0
  progressStatus.value = undefined
  statusText.value = '正在上传文件...'
  
  try {
    // 1. 上传文件
    const formData = new FormData()
    formData.append('file', selectedFile.value.raw)
    
    const uploadResponse = await fetch('/api/files/upload', {
      method: 'POST',
      body: formData
    })
    
    if (!uploadResponse.ok) {
      throw new Error('上传失败')
    }
    
    const uploadResult = await uploadResponse.json()
    statusText.value = '正在转写...'
    progress.value = 50
    
    // 2. 创建转写任务
    const taskResponse = await fetch('/api/tasks', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: `转写：${selectedFile.value.name}`,
        plugin: 'media-transcribe',
        file_path: uploadResult.file_path,
        config: config.value
      })
    })
    
    const task = await taskResponse.json()
    statusText.value = '正在处理...'
    progress.value = 70
    
    // 3. 执行插件
    const executeResponse = await fetch(`/api/plugins/media-transcribe/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        file_path: uploadResult.file_path,
        model_size: config.value.modelSize,
        language: config.value.language === 'auto' ? undefined : config.value.language,
        output_format: config.value.outputFormat
      })
    })
    
    if (!executeResponse.ok) {
      const error = await executeResponse.json()
      throw new Error(error.detail || '转写失败')
    }
    
    const executeResult = await executeResponse.json()
    progress.value = 100
    progressStatus.value = 'success'
    statusText.value = '转写完成!'
    transcribing.value = false
    
    // 显示结果
    if (executeResult.text) {
      result.value = executeResult.text
    } else if (executeResult.output) {
      result.value = executeResult.output
    } else {
      result.value = JSON.stringify(executeResult, null, 2)
    }
    
  } catch (error: any) {
    progressStatus.value = 'exception'
    statusText.value = `错误：${error.message}`
    transcribing.value = false
    result.value = `转写失败：${error.message}\n\n请确保：\n1. 文件格式支持（mp3/wav/mp4 等）\n2. 已安装 ffmpeg（可选，用于视频处理）\n3. 文件大小适中`
  }
}

const handleCopy = () => {
  navigator.clipboard.writeText(result.value)
}

const handleExport = () => {
  console.log('Export result')
}
</script>

<style scoped>
.transcribe-view h1 {
  margin-bottom: 10px;
}
</style>

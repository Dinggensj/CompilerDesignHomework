<script setup>
import { nextTick, onMounted, onUnmounted, ref } from 'vue'

const input = ref('')
const loading = ref(false)
const error = ref('')
const speechError = ref('')
const speechSupported = ref(false)
const listening = ref(false)
const speechProcessing = ref(false)
const messages = ref([
  {
    role: 'assistant',
    content:
      '你好，我是编译原理课程助手。'
  }
])
const chatBody = ref(null)

let recognition = null
let speechBaseText = ''

function getSpeechRecognitionConstructor() {
  if (typeof window === 'undefined') {
    return null
  }

  return window.SpeechRecognition || window.webkitSpeechRecognition || null
}

function setInputFromSpeech(transcript) {
  const base = speechBaseText.trim()
  const captured = transcript.trim()

  if (!base) {
    input.value = captured
    return
  }

  input.value = captured ? `${base} ${captured}` : base
}

function speechErrorMessage(code) {
  if (code === 'not-allowed' || code === 'service-not-allowed') {
    return '麦克风权限被拒绝，请在浏览器设置中允许访问麦克风。'
  }
  if (code === 'no-speech') {
    return '没有检测到语音，请靠近麦克风后重试。'
  }
  if (code === 'audio-capture') {
    return '未检测到可用麦克风设备，请检查设备连接。'
  }
  if (code === 'network') {
    return '语音识别网络异常，请稍后再试。'
  }
  return '语音识别失败，请重试。'
}

function setupRecognition() {
  const RecognitionCtor = getSpeechRecognitionConstructor()
  if (!RecognitionCtor) {
    return null
  }

  const instance = new RecognitionCtor()
  instance.lang = 'zh-CN'
  instance.interimResults = true
  instance.continuous = false
  instance.maxAlternatives = 1

  instance.onstart = () => {
    listening.value = true
    speechProcessing.value = false
    speechError.value = ''
  }

  instance.onresult = (event) => {
    let finalText = ''
    let interimText = ''

    for (let i = 0; i < event.results.length; i += 1) {
      const result = event.results[i]
      const transcript = result[0]?.transcript ?? ''
      if (result.isFinal) {
        finalText += transcript
      } else {
        interimText += transcript
      }
    }

    setInputFromSpeech(`${finalText}${interimText}`)
  }

  instance.onerror = (event) => {
    speechError.value = speechErrorMessage(event.error)
    listening.value = false
    speechProcessing.value = false
  }

  instance.onend = () => {
    listening.value = false
    speechProcessing.value = false
    speechBaseText = ''
  }

  return instance
}

function startListening() {
  if (loading.value || !speechSupported.value) {
    return
  }

  speechError.value = ''
  speechBaseText = input.value

  if (!recognition) {
    recognition = setupRecognition()
  }

  if (!recognition) {
    speechSupported.value = false
    speechError.value = '当前浏览器不支持语音输入，请使用键盘输入。'
    return
  }

  try {
    recognition.start()
  } catch {
    speechError.value = '语音识别启动失败，请稍后重试。'
  }
}

function stopListening() {
  if (!recognition || !listening.value) {
    return
  }

  speechProcessing.value = true
  try {
    recognition.stop()
  } catch {
    speechProcessing.value = false
  }
}

function toggleListening() {
  if (listening.value) {
    stopListening()
  } else {
    startListening()
  }
}

async function scrollToBottom() {
  await nextTick()
  if (chatBody.value) {
    chatBody.value.scrollTop = chatBody.value.scrollHeight
  }
}

async function sendMessage() {
  const content = input.value.trim()
  if (!content || loading.value) {
    return
  }

  if (listening.value) {
    stopListening()
  }

  messages.value.push({ role: 'user', content })
  input.value = ''
  error.value = ''
  speechError.value = ''
  loading.value = true
  await scrollToBottom()

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages: messages.value
          .filter((message, index) => index > 0 && message.role !== 'system')
          .map((message) => ({
            role: message.role,
            content: message.content
          }))
      })
    })

    const data = await response.json()
    if (!response.ok) {
      throw new Error(data.detail || '请求失败，请稍后重试。')
    }

    messages.value.push({ role: 'assistant', content: data.reply })
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}

function handleKeydown(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

onMounted(() => {
  speechSupported.value = Boolean(getSpeechRecognitionConstructor())
})

onUnmounted(() => {
  if (!recognition) {
    return
  }

  recognition.onstart = null
  recognition.onresult = null
  recognition.onerror = null
  recognition.onend = null
  recognition.abort()
  recognition = null
})
</script>

<template>
  <main class="page">
    <header class="page__header">
      <p class="page__eyebrow">Homework 6</p>
      <h1 class="page__title">AI 对话助手</h1>
    </header>
    <section class="chat" aria-label="AI 对话">
      <div ref="chatBody" class="chat__body">
        <article
          v-for="(message, index) in messages"
          :key="index"
          class="message"
          :class="`message--${message.role}`"
        >
          <span class="message__name">{{ message.role === 'user' ? '我' : 'AI' }}</span>
          <p>{{ message.content }}</p>
        </article>
        <article v-if="loading" class="message message--assistant">
          <span class="message__name">AI</span>
          <p>正在思考中...</p>
        </article>
      </div>

      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="speechError" class="error error--speech">{{ speechError }}</p>

      <form class="composer" @submit.prevent="sendMessage">
        <textarea
          v-model="input"
          rows="3"
          placeholder="请输入消息"
          @keydown="handleKeydown"
        ></textarea>

        <div class="composer__actions">
          <button
            type="button"
            class="button button--secondary"
            :disabled="loading || !speechSupported || speechProcessing"
            @click="toggleListening"
          >
            {{ listening ? '停止语音' : '语音输入' }}
          </button>
          <button type="submit" class="button button--primary" :disabled="loading || !input.trim()">
            {{ loading ? '发送中' : '发送' }}
          </button>
        </div>

        <p class="speech-tip">
          {{ !speechSupported ? '当前浏览器不支持语音输入，可继续手动输入。' : '' }}
          {{ listening ? '正在听写，请点击“停止语音”结束。' : '' }}
          {{ speechProcessing ? '正在整理语音识别结果...' : '' }}
          {{ !listening && !speechProcessing && speechSupported ? '点击“语音输入”开始识别。' : '' }}
        </p>
      </form>
    </section>
  </main>
</template>

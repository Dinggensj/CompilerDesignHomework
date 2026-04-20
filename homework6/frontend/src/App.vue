<script setup>
import { nextTick, ref } from 'vue'

const input = ref('')
const loading = ref(false)
const error = ref('')
const messages = ref([
  {
    role: 'assistant',
    content: '你好，我是编译原理课程助手。可以问我词法分析、语法分析、FIRST/FOLLOW 集或实验代码问题。'
  }
])
const chatBody = ref(null)

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

  messages.value.push({ role: 'user', content })
  input.value = ''
  error.value = ''
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
      throw new Error(data.detail || '请求失败，请稍后再试。')
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
</script>

<template>
  <main class="page">
    <section class="intro">
      <img
        class="intro__image"
        src="https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=900&q=80"
        alt="桌面上的笔记本电脑"
      />
      <div>
        <p class="eyebrow">Homework 6</p>
        <h1>AI 对话助手</h1>
        <p class="intro__copy">把编译原理的问题写下来，马上开始一轮清爽的问答。</p>
      </div>
    </section>

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

      <form class="composer" @submit.prevent="sendMessage">
        <textarea
          v-model="input"
          rows="3"
          placeholder="例如：LL(1) 文法为什么要消除左递归？"
          @keydown="handleKeydown"
        ></textarea>
        <button type="submit" :disabled="loading || !input.trim()">
          {{ loading ? '发送中' : '发送' }}
        </button>
      </form>
    </section>
  </main>
</template>

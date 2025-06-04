<script lang="ts" setup>
import { ref } from 'vue'

const query = ref('')
const isLoading = ref(false)
const answer = ref('')
const error = ref('')

async function handleSubmit() {
  if (!query.value.trim())
    return

  isLoading.value = true
  error.value = ''
  answer.value = ''

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query: query.value.trim() }),
    })

    if (!response.ok)
      throw new Error(`HTTP error! status: ${response.status}`)

    const data = await response.json()
    if (data.error)
      error.value = data.error
    else
      answer.value = data.answer
  }
  catch (err: any) {
    error.value = `Error: ${err.message}`
    console.error('Chat error:', err)
  }
  finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="chat-container mb-8">
    <form class="flex gap-2" @submit.prevent="handleSubmit">
      <input
        v-model="query"
        type="text"
        placeholder="Ask a question..."
        class="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        :disabled="isLoading"
        @keyup.enter="handleSubmit"
      >
      <button
        type="button"
        class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
        :disabled="isLoading"
        @click="handleSubmit"
      >
        {{ isLoading ? 'Thinking...' : 'Ask' }}
      </button>
    </form>

    <div v-if="error" class="mt-4 p-4 rounded-lg bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200">
      {{ error }}
    </div>

    <div v-if="answer" class="mt-4 p-4 rounded-lg bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100">
      {{ answer }}
    </div>
  </div>
</template>

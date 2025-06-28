<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          NumWatch Dashboard
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Sign in to access your lottery analysis
        </p>
      </div>
      
      <!-- Login Form -->
      <form v-if="!showRegister" @submit.prevent="login" class="mt-8 space-y-6">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Username</label>
            <input
              v-model="loginData.username"
              type="text"
              required
              class="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your username"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Password</label>
            <input
              v-model="loginData.password"
              type="password"
              required
              class="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your password"
            />
          </div>
        </div>
        
        <div v-if="error" class="text-red-600 text-sm text-center">
          {{ error }}
        </div>
        
        <div>
          <button
            type="submit"
            :disabled="loading"
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {{ loading ? 'Signing in...' : 'Sign in' }}
          </button>
        </div>
        
        <div class="text-center">
          <button
            type="button"
            @click="showRegister = true"
            class="text-blue-600 hover:text-blue-500 text-sm"
          >
            Don't have an account? Register here
          </button>
        </div>
      </form>
      
      <!-- Register Form -->
      <form v-else @submit.prevent="register" class="mt-8 space-y-6">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Username</label>
            <input
              v-model="registerData.username"
              type="text"
              required
              class="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Choose a username"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Email</label>
            <input
              v-model="registerData.email"
              type="email"
              required
              class="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your email"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Password</label>
            <input
              v-model="registerData.password"
              type="password"
              required
              class="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Choose a password"
            />
          </div>
        </div>
        
        <div v-if="error" class="text-red-600 text-sm text-center">
          {{ error }}
        </div>
        
        <div>
          <button
            type="submit"
            :disabled="loading"
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
          >
            {{ loading ? 'Creating account...' : 'Create account' }}
          </button>
        </div>
        
        <div class="text-center">
          <button
            type="button"
            @click="showRegister = false"
            class="text-blue-600 hover:text-blue-500 text-sm"
          >
            Already have an account? Sign in here
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '../services/api'

const router = useRouter()

const showRegister = ref(false)
const loading = ref(false)
const error = ref('')

const loginData = ref({ username: '', password: '' })
const registerData = ref({ username: '', email: '', password: '' })

const login = async () => {
  try {
    loading.value = true
    error.value = ''
    
    const response = await authApi.login(loginData.value)
    localStorage.setItem('auth_token', response.access_token)
    
    router.push('/')
  } catch (err) {
    error.value = 'Invalid username or password'
  } finally {
    loading.value = false
  }
}

const register = async () => {
  try {
    loading.value = true
    error.value = ''
    
    await authApi.register(registerData.value)
    showRegister.value = false
    error.value = ''
    // Show success message or auto-login
  } catch (err) {
    error.value = 'Registration failed. Username or email may already exist.'
  } finally {
    loading.value = false
  }
}
</script>
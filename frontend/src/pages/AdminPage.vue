<template>
  <div class="bg-white rounded-lg shadow-md p-6 mb-6">
    <h2 class="text-xl font-bold text-gray-800 mb-6">Admin Panel</h2>
    
    <!-- Invite Codes Section -->
    <div class="mb-8">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-gray-800">Invite Codes</h3>
        <button
          @click="showCreateForm = true"
          class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
        >
          Create Invite Code
        </button>
      </div>
      
      <div class="overflow-x-auto">
        <table class="min-w-full bg-white border border-gray-200 rounded">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Used By</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Expires</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="code in inviteCodes" :key="code.id" class="hover:bg-gray-50">
              <td class="px-3 py-2 text-sm font-mono text-gray-900">{{ code.code }}</td>
              <td class="px-3 py-2 text-sm">
                <span :class="code.is_used ? 'text-red-600' : 'text-green-600'">
                  {{ code.is_used ? 'Used' : 'Available' }}
                </span>
              </td>
              <td class="px-3 py-2 text-sm text-gray-600">
                {{ code.used_by ? getUserById(code.used_by)?.username || 'Unknown' : '-' }}
              </td>
              <td class="px-3 py-2 text-sm text-gray-600">
                {{ code.expires_at ? formatDate(code.expires_at) : 'Never' }}
              </td>
              <td class="px-3 py-2 text-sm text-gray-600">
                {{ formatDate(code.created_at) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Users Section -->
    <div>
      <h3 class="text-lg font-semibold text-gray-800 mb-4">Users</h3>
      <div class="overflow-x-auto">
        <table class="min-w-full bg-white border border-gray-200 rounded">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Username</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Last Login</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50">
              <td class="px-3 py-2 text-sm text-gray-900">{{ user.username }}</td>
              <td class="px-3 py-2 text-sm text-gray-600">{{ user.email }}</td>
              <td class="px-3 py-2 text-sm">
                <span :class="user.is_admin ? 'text-blue-600 font-medium' : 'text-gray-600'">
                  {{ user.is_admin ? 'Admin' : 'User' }}
                </span>
              </td>
              <td class="px-3 py-2 text-sm text-gray-600">
                {{ user.last_login ? formatDate(user.last_login) : 'Never' }}
              </td>
              <td class="px-3 py-2 text-sm text-gray-600">
                {{ formatDate(user.created_at) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Create Invite Code Modal -->
    <div v-if="showCreateForm" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded-lg max-w-md w-full mx-4">
        <h3 class="text-xl font-bold mb-4">Create Invite Code</h3>
        <form @submit.prevent="createInviteCode">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">Expiration (Optional)</label>
            <input
              v-model="newInviteExpiry"
              type="datetime-local"
              class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p class="text-xs text-gray-500 mt-1">Leave empty for no expiration</p>
          </div>
          
          <div v-if="error" class="text-red-600 text-sm mb-4">
            {{ error }}
          </div>
          
          <div class="flex gap-3">
            <button
              type="submit"
              :disabled="loading"
              class="flex-1 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
            >
              {{ loading ? 'Creating...' : 'Create Code' }}
            </button>
            <button
              type="button"
              @click="showCreateForm = false"
              class="flex-1 px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminApi } from '../services/api'
import type { User } from '../types'

interface InviteCode {
  id: number
  code: string
  created_by: number
  used_by: number | null
  is_used: boolean
  expires_at: string | null
  created_at: string
}

const inviteCodes = ref<InviteCode[]>([])
const users = ref<User[]>([])
const showCreateForm = ref(false)
const newInviteExpiry = ref('')
const loading = ref(false)
const error = ref('')

const fetchInviteCodes = async () => {
  try {
    inviteCodes.value = await adminApi.getInviteCodes()
  } catch (err) {
    console.error('Failed to fetch invite codes:', err)
  }
}

const fetchUsers = async () => {
  try {
    users.value = await adminApi.getUsers()
  } catch (err) {
    console.error('Failed to fetch users:', err)
  }
}

const createInviteCode = async () => {
  try {
    loading.value = true
    error.value = ''
    
    const inviteData = {
      expires_at: newInviteExpiry.value || null
    }
    
    await adminApi.createInviteCode(inviteData)
    await fetchInviteCodes()
    
    showCreateForm.value = false
    newInviteExpiry.value = ''
  } catch (err) {
    error.value = 'Failed to create invite code'
  } finally {
    loading.value = false
  }
}

const getUserById = (userId: number) => {
  return users.value.find(u => u.id === userId)
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(async () => {
  await Promise.all([fetchInviteCodes(), fetchUsers()])
})
</script>
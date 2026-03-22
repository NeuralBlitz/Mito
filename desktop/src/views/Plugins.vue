<template>
  <div class="content-area">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
      <h1 class="page-title" style="margin-bottom: 0;">Plugins</h1>
      <button class="btn btn-primary" @click="showModal = true">+ Add Plugin</button>
    </div>
    
    <div class="tabs">
      <div class="tab" :class="{ active: activeTab === 'all' }" @click="activeTab = 'all'">
        All ({{ plugins.length }})
      </div>
      <div class="tab" :class="{ active: activeTab === 'enabled' }" @click="activeTab = 'enabled'">
        Enabled ({{ enabledPlugins.length }})
      </div>
      <div class="tab" :class="{ active: activeTab === 'disabled' }" @click="activeTab = 'disabled'">
        Disabled ({{ disabledPlugins.length }})
      </div>
    </div>
    
    <div v-if="displayedPlugins.length === 0" class="empty-state">
      <div class="empty-icon">🧩</div>
      <p>No plugins found</p>
      <button class="btn btn-secondary" style="margin-top: 1rem;" @click="showModal = true">
        Install a Plugin
      </button>
    </div>
    
    <div v-else>
      <div v-for="plugin in displayedPlugins" :key="plugin.id" class="plugin-item">
        <div class="plugin-info">
          <div class="plugin-icon">🔌</div>
          <div>
            <div class="plugin-name">{{ plugin.name }}</div>
            <div class="plugin-version">v{{ plugin.version }} by {{ plugin.author }}</div>
            <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.25rem;">
              {{ plugin.description }}
            </div>
          </div>
        </div>
        <label class="plugin-toggle">
          <input 
            type="checkbox" 
            :checked="plugin.enabled"
            @change="togglePlugin(plugin.id, ($event.target as HTMLInputElement).checked)"
          />
          <span class="slider"></span>
        </label>
      </div>
    </div>
    
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">Add Plugin</h3>
          <button class="modal-close" @click="showModal = false">&times;</button>
        </div>
        
        <div class="form-group">
          <label class="form-label">Plugin Name</label>
          <input type="text" class="form-input" v-model="newPlugin.name" />
        </div>
        
        <div class="form-group">
          <label class="form-label">Version</label>
          <input type="text" class="form-input" v-model="newPlugin.version" placeholder="1.0.0" />
        </div>
        
        <div class="form-group">
          <label class="form-label">Description</label>
          <textarea class="form-input" v-model="newPlugin.description"></textarea>
        </div>
        
        <div class="form-group">
          <label class="form-label">Author</label>
          <input type="text" class="form-input" v-model="newPlugin.author" />
        </div>
        
        <button class="btn btn-primary" style="width: 100%;" @click="registerPlugin">
          Install Plugin
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { useAppStore } from '@/stores/app'

const store = useAppStore()

const activeTab = ref('all')
const showModal = ref(false)
const newPlugin = reactive({
  name: '',
  version: '1.0.0',
  description: '',
  author: ''
})

const plugins = computed(() => store.plugins)
const enabledPlugins = computed(() => store.enabledPlugins)
const disabledPlugins = computed(() => store.disabledPlugins)

const displayedPlugins = computed(() => {
  if (activeTab.value === 'enabled') return enabledPlugins.value
  if (activeTab.value === 'disabled') return disabledPlugins.value
  return plugins.value
})

async function togglePlugin(id: string, enabled: boolean) {
  if (enabled) {
    await store.enablePlugin(id)
  } else {
    await store.disablePlugin(id)
  }
}

async function registerPlugin() {
  if (newPlugin.name && newPlugin.version) {
    await store.registerPlugin(
      newPlugin.name,
      newPlugin.version,
      newPlugin.description,
      newPlugin.author,
      []
    )
    newPlugin.name = ''
    newPlugin.version = '1.0.0'
    newPlugin.description = ''
    newPlugin.author = ''
    showModal.value = false
  }
}
</script>

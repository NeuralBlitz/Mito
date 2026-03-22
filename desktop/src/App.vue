<template>
  <div class="app-container">
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="logo">
          <div class="logo-icon">M</div>
          <span class="logo-text">Mito</span>
        </div>
      </div>
      
      <nav class="nav-menu">
        <div class="nav-section">
          <div class="nav-section-title">Main</div>
          <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
            <span class="nav-icon">📊</span>
            <span>Dashboard</span>
          </router-link>
          <router-link to="/commands" class="nav-item" :class="{ active: $route.path === '/commands' }">
            <span class="nav-icon">⚡</span>
            <span>Commands</span>
          </router-link>
          <router-link to="/terminal" class="nav-item" :class="{ active: $route.path === '/terminal' }">
            <span class="nav-icon">💻</span>
            <span>Terminal</span>
          </router-link>
        </div>
        
        <div class="nav-section">
          <div class="nav-section-title">Extensions</div>
          <router-link to="/plugins" class="nav-item" :class="{ active: $route.path === '/plugins' }">
            <span class="nav-icon">🧩</span>
            <span>Plugins</span>
          </router-link>
          <router-link to="/os" class="nav-item" :class="{ active: $route.path === '/os' }">
            <span class="nav-icon">🔄<span>OS Swap</span>
            </span>
          </router-link>
        </div>
        
        <div class="nav-section">
          <div class="nav-section-title">System</div>
          <router-link to="/settings" class="nav-item" :class="{ active: $route.path === '/settings' }">
            <span class="nav-icon">⚙️</span>
            <span>Settings</span>
          </router-link>
        </div>
      </nav>
      
      <div class="sidebar-footer">
        <div class="nav-item" style="cursor: default;">
          <span class="nav-icon">💜</span>
          <span>v{{ appInfo?.version || '1.0.0' }}</span>
        </div>
      </div>
    </aside>
    
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useAppStore } from '@/stores/app'

const store = useAppStore()

const appInfo = computed(() => store.appInfo)

onMounted(async () => {
  await store.loadAppInfo()
  await store.loadCommands()
  await store.loadPlugins()
})
</script>

<style scoped>
.sidebar-footer {
  border-top: 1px solid var(--border);
  padding-top: 1rem;
  margin-top: auto;
}
</style>

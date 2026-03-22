<template>
  <div class="content-area">
    <h1 class="page-title">Dashboard</h1>
    
    <div class="grid grid-4" style="margin-bottom: 1.5rem;">
      <div class="stat-card">
        <div class="stat-value">{{ commands.length }}</div>
        <div class="stat-label">Commands</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ plugins.length }}</div>
        <div class="stat-label">Plugins</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ enabledPlugins }}</div>
        <div class="stat-label">Active Plugins</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">99.9%</div>
        <div class="stat-label">Uptime</div>
      </div>
    </div>
    
    <div class="grid grid-2">
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Quick Actions</h3>
        </div>
        <div class="command-list">
          <div 
            v-for="cmd in quickCommands" 
            :key="cmd.name" 
            class="command-item"
            @click="runQuickCommand(cmd.name)"
          >
            <div class="command-name">{{ cmd.name }}</div>
            <div class="command-desc">{{ cmd.description }}</div>
          </div>
        </div>
      </div>
      
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">System Status</h3>
        </div>
        <div style="padding: 0.5rem 0;">
          <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid var(--border);">
            <span>CPU</span>
            <span class="badge badge-success">23%</span>
          </div>
          <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid var(--border);">
            <span>Memory</span>
            <span class="badge badge-success">4.2 GB</span>
          </div>
          <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid var(--border);">
            <span>Storage</span>
            <span class="badge badge-warning">67%</span>
          </div>
          <div style="display: flex; justify-content: space-between; padding: 0.5rem 0;">
            <span>API Server</span>
            <span class="badge badge-success">Running</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="card" style="margin-top: 1rem;">
      <div class="card-header">
        <h3 class="card-title">Recent Activity</h3>
      </div>
      <div class="terminal" style="max-height: 200px;">
        <div v-for="(line, i) in terminalOutput.slice(-10)" :key="i" class="terminal-output">
          {{ line }}
        </div>
        <div v-if="terminalOutput.length === 0" style="color: var(--text-secondary);">
          No recent activity. Run a command to see output here.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'

const store = useAppStore()
const router = useRouter()

const commands = computed(() => store.commands)
const plugins = computed(() => store.plugins)
const enabledPlugins = computed(() => store.enabledPlugins.length)
const terminalOutput = computed(() => store.terminalOutput)

const quickCommands = computed(() => store.commands.slice(0, 6))

async function runQuickCommand(name: string) {
  await store.runCommand(name, [])
  router.push('/terminal')
}
</script>

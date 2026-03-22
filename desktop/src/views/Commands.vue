<template>
  <div class="content-area">
    <h1 class="page-title">Commands</h1>
    
    <div class="tabs">
      <div 
        v-for="(cmds, category) in commandsByCategory" 
        :key="category"
        class="tab"
        :class="{ active: selectedCategory === category }"
        @click="selectedCategory = category"
      >
        {{ category }} ({{ cmds.length }})
      </div>
    </div>
    
    <div class="command-list">
      <div 
        v-for="cmd in selectedCommands" 
        :key="cmd.name" 
        class="command-item"
        @click="openCommandModal(cmd)"
      >
        <div class="command-name">{{ cmd.name }}</div>
        <div class="command-desc">{{ cmd.description }}</div>
      </div>
    </div>
    
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">{{ selectedCommand?.name }}</h3>
          <button class="modal-close" @click="showModal = false">&times;</button>
        </div>
        
        <p style="color: var(--text-secondary); margin-bottom: 1rem;">
          {{ selectedCommand?.description }}
        </p>
        
        <div class="form-group" v-for="arg in selectedCommand?.args" :key="arg.name">
          <label class="form-label">
            {{ arg.name }}
            <span v-if="!arg.required" style="color: var(--text-secondary);">(optional)</span>
          </label>
          <input 
            type="text" 
            class="form-input"
            v-model="argValues[arg.name]"
            :placeholder="arg.default || ''"
          />
        </div>
        
        <button class="btn btn-primary" style="width: 100%;" @click="executeSelectedCommand">
          Execute
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'

const store = useAppStore()
const router = useRouter()

const selectedCategory = ref('core')
const showModal = ref(false)
const selectedCommand = ref<any>(null)
const argValues = reactive<Record<string, string>>({})

const commands = computed(() => store.commands)
const commandsByCategory = computed(() => store.commandsByCategory)

const selectedCommands = computed(() => {
  return commandsByCategory.value[selectedCategory.value] || []
})

function openCommandModal(cmd: any) {
  selectedCommand.value = cmd
  Object.keys(argValues).forEach(key => delete argValues[key])
  cmd.args.forEach((arg: any) => {
    argValues[arg.name] = arg.default || ''
  })
  showModal.value = true
}

async function executeSelectedCommand() {
  if (selectedCommand.value) {
    await store.runCommand(selectedCommand.value.name, Object.values(argValues).filter(Boolean))
    showModal.value = false
    router.push('/terminal')
  }
}
</script>

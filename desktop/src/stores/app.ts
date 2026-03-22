import { defineStore } from 'pinia'
import { invoke } from '@tauri-apps/api/tauri'

interface Command {
  name: string
  description: string
  category: string
  args: Array<{
    name: string
    required: boolean
    default: string | null
  }>
}

interface Plugin {
  id: string
  name: string
  version: string
  description: string
  author: string
  enabled: boolean
  permissions: string[]
}

interface AppInfo {
  version: string
  name: string
  description: string
}

export const useAppStore = defineStore('app', {
  state: () => ({
    appInfo: null as AppInfo | null,
    commands: [] as Command[],
    plugins: [] as Plugin[],
    loading: false,
    error: null as string | null,
    terminalOutput: [] as string[]
  }),

  actions: {
    async loadAppInfo() {
      try {
        this.appInfo = await invoke('get_app_info')
      } catch (e) {
        console.error('Failed to load app info:', e)
        this.appInfo = { version: '1.0.0', name: 'Mito', description: 'AI Toolkit' }
      }
    },

    async loadCommands() {
      try {
        this.commands = await invoke('list_commands')
      } catch (e) {
        console.error('Failed to load commands:', e)
      }
    },

    async loadPlugins() {
      try {
        this.plugins = await invoke('list_plugins')
      } catch (e) {
        console.error('Failed to load plugins:', e)
      }
    },

    async executeCommand(command: string, args: Record<string, string>) {
      this.loading = true
      this.error = null
      try {
        const result = await invoke('execute_command', { command, args })
        this.terminalOutput.push(`$ mito ${command} ${Object.values(args).join(' ')}`)
        this.terminalOutput.push(result as string)
        return result
      } catch (e) {
        this.error = e as string
        this.terminalOutput.push(`Error: ${e}`)
      } finally {
        this.loading = false
      }
    },

    async runCommand(command: string, args: string[]) {
      this.loading = true
      try {
        const result = await invoke('run_mito_command', { command, args })
        this.terminalOutput.push(`$ mito ${command} ${args.join(' ')}`)
        this.terminalOutput.push(result as string)
        return result
      } catch (e) {
        this.terminalOutput.push(`Error: ${e}`)
      } finally {
        this.loading = false
      }
    },

    async enablePlugin(id: string) {
      try {
        await invoke('enable_plugin', { id })
        const plugin = this.plugins.find(p => p.id === id)
        if (plugin) plugin.enabled = true
      } catch (e) {
        console.error('Failed to enable plugin:', e)
      }
    },

    async disablePlugin(id: string) {
      try {
        await invoke('disable_plugin', { id })
        const plugin = this.plugins.find(p => p.id === id)
        if (plugin) plugin.enabled = false
      } catch (e) {
        console.error('Failed to disable plugin:', e)
      }
    },

    async registerPlugin(name: string, version: string, description: string, author: string, permissions: string[]) {
      try {
        const plugin = await invoke('register_plugin', { name, version, description, author, permissions })
        this.plugins.push(plugin as Plugin)
      } catch (e) {
        console.error('Failed to register plugin:', e)
      }
    },

    clearTerminal() {
      this.terminalOutput = []
    }
  },

  getters: {
    commandsByCategory: (state) => {
      const categories: Record<string, Command[]> = {}
      state.commands.forEach(cmd => {
        if (!categories[cmd.category]) {
          categories[cmd.category] = []
        }
        categories[cmd.category].push(cmd)
      })
      return categories
    },

    enabledPlugins: (state) => state.plugins.filter(p => p.enabled),
    disabledPlugins: (state) => state.plugins.filter(p => !p.enabled)
  }
})

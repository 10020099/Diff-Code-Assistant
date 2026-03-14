/**
 * 设置 Store - 管理 API 提供商配置
 */

import { create } from 'zustand'

export type LLMProvider = 'openai' | 'openai-responses' | 'claude' | 'gemini' | 'deepseek'

export interface ProviderConfig {
  id: string
  name: string
  provider: LLMProvider
  apiKey: string
  baseUrl: string
  model: string
  maxTokens?: number
  temperature?: number
}

export interface AppConfig {
  providers: ProviderConfig[]
  activeProviderId: string | null
  systemPrompt: string
}

interface SettingsState {
  config: AppConfig
  isLoading: boolean

  // Actions
  setConfig: (config: AppConfig) => void
  addProvider: (provider: ProviderConfig) => void
  updateProvider: (id: string, updates: Partial<ProviderConfig>) => void
  removeProvider: (id: string) => void
  setActiveProvider: (id: string | null) => void
  setSystemPrompt: (prompt: string) => void
  getActiveProvider: () => ProviderConfig | null
  setIsLoading: (loading: boolean) => void

  // 持久化
  loadConfig: () => Promise<void>
  saveConfig: () => Promise<void>
}

const DEFAULT_SYSTEM_PROMPT = `你是一个专业的代码修改助手，正在通过一个桌面工具与用户进行多轮对话。

## 工作模式
- 用户的第一条消息通常会包含项目的文件结构和代码内容作为上下文
- 用户会用自然语言描述他们想要的代码修改
- 你需要理解需求，生成精确的代码修改，并以 unified diff 格式输出
- 用户可能会在后续消息中追加修改、调整要求或提出新需求，请基于之前的对话上下文继续工作

## 输出规则

### 1. Diff 格式要求
所有代码修改**必须**放在 \\\`\\\`\\\`diff 代码块中，这样工具才能自动提取和应用：

\\\`\\\`\\\`diff
--- a/src/example.ts
+++ b/src/example.ts
@@ -10,7 +10,7 @@
 import { foo } from './utils'
 
-const oldValue = 'hello'
+const newValue = 'world'
 
 export function main() {
\\\`\\\`\\\`

### 2. 格式细节
- 每个文件用独立的 \`---\` 和 \`+++\` 头，路径使用 \`a/\` 和 \`b/\` 前缀
- hunk 头格式: \`@@ -旧起始行,旧行数 +新起始行,新行数 @@\`
- 上下文行（不变的行）以空格开头，保留 3 行上下文
- 删除行以 \`-\` 开头，添加行以 \`+\` 开头
- 新建文件使用 \`--- /dev/null\`，删除文件使用 \`+++ /dev/null\`
- 如果修改涉及多个文件，所有 diff 放在**同一个** \\\`\\\`\\\`diff 代码块中

### 3. 回复风格
- 先简要说明你要做什么修改以及为什么
- 然后给出 diff 代码块
- 如果修改较复杂，可以在 diff 后补充关键说明
- 如果用户的需求不明确，先询问澄清再生成 diff
- 回复使用中文`

export const useSettingsStore = create<SettingsState>((set, get) => ({
  config: {
    providers: [],
    activeProviderId: null,
    systemPrompt: DEFAULT_SYSTEM_PROMPT
  },
  isLoading: false,

  setConfig: (config) => set({ config }),

  addProvider: (provider) => {
    const { config } = get()
    const newConfig = {
      ...config,
      providers: [...config.providers, provider]
    }
    // 如果是第一个提供商，自动设为活跃
    if (!config.activeProviderId) {
      newConfig.activeProviderId = provider.id
    }
    set({ config: newConfig })
  },

  updateProvider: (id, updates) => {
    const { config } = get()
    set({
      config: {
        ...config,
        providers: config.providers.map(p =>
          p.id === id ? { ...p, ...updates } : p
        )
      }
    })
  },

  removeProvider: (id) => {
    const { config } = get()
    const newProviders = config.providers.filter(p => p.id !== id)
    set({
      config: {
        ...config,
        providers: newProviders,
        activeProviderId: config.activeProviderId === id
          ? (newProviders[0]?.id || null)
          : config.activeProviderId
      }
    })
  },

  setActiveProvider: (id) => {
    const { config } = get()
    set({ config: { ...config, activeProviderId: id } })
  },

  setSystemPrompt: (prompt) => {
    const { config } = get()
    set({ config: { ...config, systemPrompt: prompt } })
  },

  getActiveProvider: () => {
    const { config } = get()
    if (!config.activeProviderId) return null
    return config.providers.find(p => p.id === config.activeProviderId) || null
  },

  setIsLoading: (loading) => set({ isLoading: loading }),

  loadConfig: async () => {
    set({ isLoading: true })
    try {
      const result = await (window as any).api.config.load()
      if (result.success && result.data) {
        set({
          config: {
            ...result.data,
            systemPrompt: result.data.systemPrompt || DEFAULT_SYSTEM_PROMPT
          }
        })
      }
    } catch (error) {
      console.error('加载配置失败:', error)
    } finally {
      set({ isLoading: false })
    }
  },

  saveConfig: async () => {
    try {
      const { config } = get()
      await (window as any).api.config.save(config)
    } catch (error) {
      console.error('保存配置失败:', error)
    }
  }
}))

/**
 * LLM 统一类型定义
 */

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

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant'
  content: string
  timestamp?: number
}

export interface ChatRequest {
  providerId: string
  messages: ChatMessage[]
  systemPrompt?: string
  stream?: boolean
}

export interface ChatResponse {
  success: boolean
  content?: string
  error?: string
  usage?: {
    promptTokens: number
    completionTokens: number
    totalTokens: number
  }
}

export interface StreamEvent {
  type: 'token' | 'done' | 'error'
  content?: string
  error?: string
  usage?: {
    promptTokens: number
    completionTokens: number
    totalTokens: number
  }
}

// 对话历史
export interface Conversation {
  id: string
  title: string
  projectRoot: string | null
  messages: ChatMessage[]
  createdAt: number
  updatedAt: number
}

// 应用配置
export interface AppConfig {
  providers: ProviderConfig[]
  activeProviderId: string | null
  systemPrompt: string
}

// 默认提供商配置
export const DEFAULT_PROVIDERS: Omit<ProviderConfig, 'id' | 'apiKey'>[] = [
  {
    name: 'OpenAI',
    provider: 'openai',
    baseUrl: 'https://api.openai.com/v1',
    model: 'gpt-4o',
  },
  {
    name: 'OpenAI Responses',
    provider: 'openai-responses',
    baseUrl: 'https://api.openai.com/v1',
    model: 'gpt-4o',
  },
  {
    name: 'Claude',
    provider: 'claude',
    baseUrl: 'https://api.anthropic.com',
    model: 'claude-sonnet-4-20250514',
  },
  {
    name: 'Gemini',
    provider: 'gemini',
    baseUrl: 'https://generativelanguage.googleapis.com',
    model: 'gemini-2.5-flash',
  },
  {
    name: 'DeepSeek',
    provider: 'deepseek',
    baseUrl: 'https://api.deepseek.com',
    model: 'deepseek-chat',
  }
]

export const DEFAULT_SYSTEM_PROMPT = `你是一个专业的代码修改助手，正在通过一个桌面工具与用户进行多轮对话。

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

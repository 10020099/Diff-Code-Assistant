/**
 * 聊天 Store - 管理对话状态、消息列表、流式响应
 */

import { create } from 'zustand'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: number
  // 从 AI 回复中提取的 diff 块
  diffBlocks?: string[]
}

export interface ConversationSummary {
  id: string
  title: string
  projectRoot: string | null
  messageCount: number
  createdAt: number
  updatedAt: number
}

export interface Conversation {
  id: string
  title: string
  projectRoot: string | null
  messages: ChatMessage[]
  createdAt: number
  updatedAt: number
}

interface ChatState {
  // 当前对话
  currentConversation: Conversation | null
  // 对话列表
  conversationList: ConversationSummary[]
  // 流式响应临时内容
  streamingContent: string
  isStreaming: boolean
  // 侧边栏
  showHistory: boolean

  // Actions
  createNewConversation: (projectRoot: string | null) => void
  setCurrentConversation: (conv: Conversation | null) => void
  addMessage: (message: ChatMessage) => void
  updateLastAssistantMessage: (content: string) => void
  setStreamingContent: (content: string) => void
  appendStreamingContent: (token: string) => void
  setIsStreaming: (streaming: boolean) => void
  finalizeStreaming: () => void
  setConversationList: (list: ConversationSummary[]) => void
  setShowHistory: (show: boolean) => void

  // 持久化
  loadConversationList: () => Promise<void>
  saveCurrentConversation: () => Promise<void>
  loadConversation: (id: string) => Promise<void>
  deleteConversation: (id: string) => Promise<void>
}

function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 8)
}

/**
 * 从 AI 回复内容中提取 ```diff 代码块
 */
export function extractDiffBlocks(content: string): string[] {
  const blocks: string[] = []
  const regex = /```diff\s*\n([\s\S]*?)```/g
  let match

  while ((match = regex.exec(content)) !== null) {
    blocks.push(match[1].trim())
  }

  return blocks
}

export const useChatStore = create<ChatState>((set, get) => ({
  currentConversation: null,
  conversationList: [],
  streamingContent: '',
  isStreaming: false,
  showHistory: false,

  createNewConversation: (projectRoot) => {
    const now = Date.now()
    const conv: Conversation = {
      id: generateId(),
      title: '新对话',
      projectRoot,
      messages: [],
      createdAt: now,
      updatedAt: now
    }
    set({ currentConversation: conv, streamingContent: '' })
  },

  setCurrentConversation: (conv) => set({ currentConversation: conv, streamingContent: '' }),

  addMessage: (message) => {
    const { currentConversation } = get()
    if (!currentConversation) return

    const updatedConv = {
      ...currentConversation,
      messages: [...currentConversation.messages, message],
      updatedAt: Date.now(),
      // 用第一条用户消息作为标题
      title: currentConversation.messages.length === 0 && message.role === 'user'
        ? message.content.slice(0, 50) + (message.content.length > 50 ? '...' : '')
        : currentConversation.title
    }
    set({ currentConversation: updatedConv })
  },

  updateLastAssistantMessage: (content) => {
    const { currentConversation } = get()
    if (!currentConversation) return

    const messages = [...currentConversation.messages]
    const lastIdx = messages.length - 1
    if (lastIdx >= 0 && messages[lastIdx].role === 'assistant') {
      messages[lastIdx] = {
        ...messages[lastIdx],
        content,
        diffBlocks: extractDiffBlocks(content)
      }
    }

    set({
      currentConversation: {
        ...currentConversation,
        messages,
        updatedAt: Date.now()
      }
    })
  },

  setStreamingContent: (content) => set({ streamingContent: content }),

  appendStreamingContent: (token) => {
    set(state => ({ streamingContent: state.streamingContent + token }))
  },

  setIsStreaming: (streaming) => set({ isStreaming: streaming }),

  finalizeStreaming: () => {
    const { streamingContent, currentConversation } = get()
    if (!currentConversation) return

    const diffBlocks = extractDiffBlocks(streamingContent)

    const assistantMessage: ChatMessage = {
      id: generateId(),
      role: 'assistant',
      content: streamingContent,
      timestamp: Date.now(),
      diffBlocks
    }

    const updatedConv = {
      ...currentConversation,
      messages: [...currentConversation.messages, assistantMessage],
      updatedAt: Date.now()
    }

    set({
      currentConversation: updatedConv,
      streamingContent: '',
      isStreaming: false
    })
  },

  setConversationList: (list) => set({ conversationList: list }),
  setShowHistory: (show) => set({ showHistory: show }),

  loadConversationList: async () => {
    try {
      const result = await (window as any).api.conversation.list()
      if (result.success && result.data) {
        set({ conversationList: result.data })
      }
    } catch (error) {
      console.error('加载对话列表失败:', error)
    }
  },

  saveCurrentConversation: async () => {
    const { currentConversation } = get()
    if (!currentConversation) return

    try {
      // 序列化重建不含 diffBlocks 的消息（减小存储体积）
      const convToSave = {
        ...currentConversation,
        messages: currentConversation.messages.map(m => ({
          id: m.id,
          role: m.role,
          content: m.content,
          timestamp: m.timestamp
        }))
      }
      await (window as any).api.conversation.save(convToSave)
      // 刷新列表
      await get().loadConversationList()
    } catch (error) {
      console.error('保存对话失败:', error)
    }
  },

  loadConversation: async (id) => {
    try {
      const result = await (window as any).api.conversation.load(id)
      if (result.success && result.data) {
        // 恢复 diffBlocks
        const conv = result.data as Conversation
        conv.messages = conv.messages.map((m: ChatMessage) => ({
          ...m,
          diffBlocks: m.role === 'assistant' ? extractDiffBlocks(m.content) : undefined
        }))
        set({ currentConversation: conv, streamingContent: '' })
      }
    } catch (error) {
      console.error('加载对话失败:', error)
    }
  },

  deleteConversation: async (id) => {
    try {
      await (window as any).api.conversation.delete(id)
      const { currentConversation } = get()
      if (currentConversation?.id === id) {
        set({ currentConversation: null })
      }
      await get().loadConversationList()
    } catch (error) {
      console.error('删除对话失败:', error)
    }
  }
}))

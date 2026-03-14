/**
 * LLM 聊天 IPC 处理器
 * 负责调用 LLM API（支持流式和非流式）
 */

import { ipcMain, BrowserWindow } from 'electron'
import { createProvider } from '../llm'
import { ProviderConfig, ChatMessage } from '../llm/types'

// 用于追踪正在进行的流式请求，以支持中断
let activeStreamAbortController: AbortController | null = null

export function registerLLMHandlers(): void {
  // 非流式聊天
  ipcMain.handle(
    'llm:chat',
    async (
      _event,
      providerConfig: ProviderConfig,
      messages: ChatMessage[],
      systemPrompt?: string
    ) => {
      try {
        const provider = createProvider(providerConfig)
        const response = await provider.chat(messages, systemPrompt)
        return response
      } catch (error) {
        return { success: false, error: String(error) }
      }
    }
  )

  // 流式聊天 - 通过 IPC events 推送 tokens
  ipcMain.handle(
    'llm:chatStream',
    async (
      event,
      providerConfig: ProviderConfig,
      messages: ChatMessage[],
      systemPrompt?: string
    ) => {
      try {
        const provider = createProvider(providerConfig)
        const window = BrowserWindow.fromWebContents(event.sender)

        if (!window) {
          return { success: false, error: '无法找到窗口' }
        }

        activeStreamAbortController = new AbortController()
        let fullContent = ''
        let aborted = false

        const generator = provider.chatStream(messages, systemPrompt)

        for await (const streamEvent of generator) {
          // 检查是否被中断
          if (activeStreamAbortController?.signal.aborted) {
            aborted = true
            break
          }

          switch (streamEvent.type) {
            case 'token':
              fullContent += streamEvent.content || ''
              // 推送 token 到渲染进程
              if (!window.isDestroyed()) {
                window.webContents.send('llm:stream-token', {
                  content: streamEvent.content
                })
              }
              break

            case 'done':
              if (!window.isDestroyed()) {
                window.webContents.send('llm:stream-done', {
                  content: fullContent,
                  usage: streamEvent.usage
                })
              }
              break

            case 'error':
              if (!window.isDestroyed()) {
                window.webContents.send('llm:stream-error', {
                  error: streamEvent.error
                })
              }
              return { success: false, error: streamEvent.error }
          }
        }

        activeStreamAbortController = null

        if (aborted) {
          if (!window.isDestroyed()) {
            window.webContents.send('llm:stream-done', {
              content: fullContent,
              aborted: true
            })
          }
        }

        return { success: true, content: fullContent }
      } catch (error) {
        activeStreamAbortController = null
        return { success: false, error: String(error) }
      }
    }
  )

  // 中断流式响应
  ipcMain.handle('llm:stopStream', () => {
    if (activeStreamAbortController) {
      activeStreamAbortController.abort()
      activeStreamAbortController = null
      return { success: true }
    }
    return { success: false, error: '没有正在进行的流式请求' }
  })

  // 测试连接
  ipcMain.handle('llm:testConnection', async (_event, providerConfig: ProviderConfig) => {
    try {
      const provider = createProvider(providerConfig)
      const result = await provider.testConnection()
      return result
    } catch (error) {
      return { success: false, message: String(error) }
    }
  })
}

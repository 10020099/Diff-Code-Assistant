/**
 * 配置管理 IPC 处理器
 * 负责持久化保存/加载 API 配置和对话历史
 */

import { ipcMain, app } from 'electron'
import * as fs from 'fs'
import * as path from 'path'
import { AppConfig, Conversation, DEFAULT_SYSTEM_PROMPT } from '../llm/types'

function getConfigDir(): string {
  return path.join(app.getPath('userData'), 'diff-code-assistant')
}

function getConfigPath(): string {
  return path.join(getConfigDir(), 'config.json')
}

function getConversationsDir(): string {
  return path.join(getConfigDir(), 'conversations')
}

function ensureDir(dirPath: string): void {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true })
  }
}

const defaultConfig: AppConfig = {
  providers: [],
  activeProviderId: null,
  systemPrompt: DEFAULT_SYSTEM_PROMPT
}

export function registerConfigHandlers(): void {
  // 保存配置
  ipcMain.handle('config:save', async (_event, config: AppConfig) => {
    try {
      ensureDir(getConfigDir())
      await fs.promises.writeFile(getConfigPath(), JSON.stringify(config, null, 2), 'utf-8')
      return { success: true }
    } catch (error) {
      return { success: false, error: String(error) }
    }
  })

  // 加载配置
  ipcMain.handle('config:load', async () => {
    try {
      const configPath = getConfigPath()
      if (!fs.existsSync(configPath)) {
        return { success: true, data: defaultConfig }
      }

      const content = await fs.promises.readFile(configPath, 'utf-8')
      const config = JSON.parse(content) as AppConfig
      return { success: true, data: config }
    } catch (error) {
      return { success: true, data: defaultConfig }
    }
  })

  // 保存对话
  ipcMain.handle('conversation:save', async (_event, conversation: Conversation) => {
    try {
      const dir = getConversationsDir()
      ensureDir(dir)
      const filePath = path.join(dir, `${conversation.id}.json`)
      await fs.promises.writeFile(filePath, JSON.stringify(conversation, null, 2), 'utf-8')
      return { success: true }
    } catch (error) {
      return { success: false, error: String(error) }
    }
  })

  // 加载所有对话列表（只返回摘要信息）
  ipcMain.handle('conversation:list', async () => {
    try {
      const dir = getConversationsDir()
      ensureDir(dir)

      const files = await fs.promises.readdir(dir)
      const conversations: Array<{
        id: string
        title: string
        projectRoot: string | null
        messageCount: number
        createdAt: number
        updatedAt: number
      }> = []

      for (const file of files) {
        if (!file.endsWith('.json')) continue
        try {
          const content = await fs.promises.readFile(path.join(dir, file), 'utf-8')
          const conv = JSON.parse(content) as Conversation
          conversations.push({
            id: conv.id,
            title: conv.title,
            projectRoot: conv.projectRoot,
            messageCount: conv.messages.length,
            createdAt: conv.createdAt,
            updatedAt: conv.updatedAt
          })
        } catch {
          // 忽略无法解析的文件
        }
      }

      // 按更新时间倒序
      conversations.sort((a, b) => b.updatedAt - a.updatedAt)

      return { success: true, data: conversations }
    } catch (error) {
      return { success: false, error: String(error) }
    }
  })

  // 加载单个对话（包含完整消息）
  ipcMain.handle('conversation:load', async (_event, conversationId: string) => {
    try {
      const filePath = path.join(getConversationsDir(), `${conversationId}.json`)
      if (!fs.existsSync(filePath)) {
        return { success: false, error: '对话不存在' }
      }

      const content = await fs.promises.readFile(filePath, 'utf-8')
      const conversation = JSON.parse(content) as Conversation
      return { success: true, data: conversation }
    } catch (error) {
      return { success: false, error: String(error) }
    }
  })

  // 删除对话
  ipcMain.handle('conversation:delete', async (_event, conversationId: string) => {
    try {
      const filePath = path.join(getConversationsDir(), `${conversationId}.json`)
      if (fs.existsSync(filePath)) {
        await fs.promises.unlink(filePath)
      }
      return { success: true }
    } catch (error) {
      return { success: false, error: String(error) }
    }
  })
}

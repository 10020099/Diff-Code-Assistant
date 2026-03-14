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

function getIndexPath(): string {
  return path.join(getConversationsDir(), '_index.json')
}

/**
 * 校验对话 ID，防止路径穿越攻击
 * 只允许字母、数字和短横线
 */
function sanitizeId(id: string): string {
  if (!/^[a-z0-9-]+$/i.test(id)) {
    throw new Error('非法的对话 ID')
  }
  return id
}

function ensureDir(dirPath: string): void {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true })
  }
}

// ===== 对话索引管理 =====

interface ConversationIndexEntry {
  id: string
  title: string
  projectRoot: string | null
  messageCount: number
  createdAt: number
  updatedAt: number
}

async function loadIndex(): Promise<ConversationIndexEntry[]> {
  const indexPath = getIndexPath()
  try {
    if (fs.existsSync(indexPath)) {
      const content = await fs.promises.readFile(indexPath, 'utf-8')
      return JSON.parse(content)
    }
  } catch {
    // 索引损坏时重建
  }
  return rebuildIndex()
}

async function saveIndex(entries: ConversationIndexEntry[]): Promise<void> {
  ensureDir(getConversationsDir())
  // 按更新时间倒序保存
  entries.sort((a, b) => b.updatedAt - a.updatedAt)
  await fs.promises.writeFile(getIndexPath(), JSON.stringify(entries, null, 2), 'utf-8')
}

/**
 * 索引损坏或不存在时，扫描所有 JSON 文件重建索引
 */
async function rebuildIndex(): Promise<ConversationIndexEntry[]> {
  const dir = getConversationsDir()
  ensureDir(dir)

  const files = await fs.promises.readdir(dir)
  const entries: ConversationIndexEntry[] = []

  for (const file of files) {
    if (!file.endsWith('.json') || file.startsWith('_')) continue
    try {
      const content = await fs.promises.readFile(path.join(dir, file), 'utf-8')
      const conv = JSON.parse(content) as Conversation
      entries.push({
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

  entries.sort((a, b) => b.updatedAt - a.updatedAt)
  await saveIndex(entries)
  return entries
}

/**
 * 更新索引中的单条记录（不存在则新增）
 */
async function updateIndexEntry(conv: Conversation): Promise<void> {
  const entries = await loadIndex()
  const entry: ConversationIndexEntry = {
    id: conv.id,
    title: conv.title,
    projectRoot: conv.projectRoot,
    messageCount: conv.messages.length,
    createdAt: conv.createdAt,
    updatedAt: conv.updatedAt
  }

  const idx = entries.findIndex(e => e.id === conv.id)
  if (idx >= 0) {
    entries[idx] = entry
  } else {
    entries.push(entry)
  }

  await saveIndex(entries)
}

/**
 * 从索引中删除记录
 */
async function removeIndexEntry(conversationId: string): Promise<void> {
  const entries = await loadIndex()
  const filtered = entries.filter(e => e.id !== conversationId)
  await saveIndex(filtered)
}

// ===== 配置默认值 =====

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

  // 保存对话（同时更新索引）
  ipcMain.handle('conversation:save', async (_event, conversation: Conversation) => {
    try {
      const dir = getConversationsDir()
      ensureDir(dir)
      const safeId = sanitizeId(conversation.id)
      const filePath = path.join(dir, `${safeId}.json`)
      await fs.promises.writeFile(filePath, JSON.stringify(conversation, null, 2), 'utf-8')

      // 更新索引
      await updateIndexEntry(conversation)

      return { success: true }
    } catch (error) {
      return { success: false, error: String(error) }
    }
  })

  // 加载对话列表（只读索引，不扫描文件内容）
  ipcMain.handle('conversation:list', async () => {
    try {
      const entries = await loadIndex()
      return { success: true, data: entries }
    } catch (error) {
      return { success: false, error: String(error) }
    }
  })

  // 加载单个对话（包含完整消息）
  ipcMain.handle('conversation:load', async (_event, conversationId: string) => {
    try {
      const safeId = sanitizeId(conversationId)
      const filePath = path.join(getConversationsDir(), `${safeId}.json`)
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

  // 删除对话（同时更新索引）
  ipcMain.handle('conversation:delete', async (_event, conversationId: string) => {
    try {
      const safeId = sanitizeId(conversationId)
      const filePath = path.join(getConversationsDir(), `${safeId}.json`)
      if (fs.existsSync(filePath)) {
        await fs.promises.unlink(filePath)
      }

      // 更新索引
      await removeIndexEntry(safeId)

      return { success: true }
    } catch (error) {
      return { success: false, error: String(error) }
    }
  })
}

import { contextBridge, ipcRenderer } from 'electron'
import { electronAPI } from '@electron-toolkit/preload'

// 文件操作 API
const fileAPI = {
  scan: (rootDir: string, options?: { excludePatterns?: string[]; maxFileSize?: number }) =>
    ipcRenderer.invoke('file:scan', rootDir, options),
  generateContext: (files: unknown[], rootDir: string, includeLineNumbers?: boolean) =>
    ipcRenderer.invoke('file:generateContext', files, rootDir, includeLineNumbers),
  getDefaultExcludePatterns: () => ipcRenderer.invoke('file:getDefaultExcludePatterns'),
  getSupportedExtensions: () => ipcRenderer.invoke('file:getSupportedExtensions')
}

// Diff 操作 API
const diffAPI = {
  validate: (diffContent: string) => ipcRenderer.invoke('diff:validate', diffContent),
  parse: (diffContent: string) => ipcRenderer.invoke('diff:parse', diffContent),
  apply: (diffContent: string, projectRoot: string, options?: { createBackup?: boolean; dryRun?: boolean }) =>
    ipcRenderer.invoke('diff:apply', diffContent, projectRoot, options),
  checkConflicts: (diffContent: string, projectRoot: string) =>
    ipcRenderer.invoke('diff:checkConflicts', diffContent, projectRoot)
}

// 备份操作 API
const backupAPI = {
  list: (projectRoot: string) => ipcRenderer.invoke('backup:list', projectRoot),
  rollback: (backupPath: string, projectRoot: string) =>
    ipcRenderer.invoke('backup:rollback', backupPath, projectRoot),
  delete: (backupPath: string) => ipcRenderer.invoke('backup:delete', backupPath),
  create: (filePaths: string[], projectRoot: string) =>
    ipcRenderer.invoke('backup:create', filePaths, projectRoot)
}

// 对话框 API
const dialogAPI = {
  openDirectory: () => ipcRenderer.invoke('dialog:openDirectory')
}

// 剪贴板 API
const clipboardAPI = {
  writeText: (text: string) => navigator.clipboard.writeText(text),
  readText: () => navigator.clipboard.readText()
}

// LLM API
const llmAPI = {
  chat: (providerConfig: unknown, messages: unknown[], systemPrompt?: string) =>
    ipcRenderer.invoke('llm:chat', providerConfig, messages, systemPrompt),
  chatStream: (providerConfig: unknown, messages: unknown[], systemPrompt?: string) =>
    ipcRenderer.invoke('llm:chatStream', providerConfig, messages, systemPrompt),
  stopStream: () => ipcRenderer.invoke('llm:stopStream'),
  testConnection: (providerConfig: unknown) =>
    ipcRenderer.invoke('llm:testConnection', providerConfig),
  // 流式事件监听
  onStreamToken: (callback: (data: { content: string }) => void) => {
    const handler = (_event: unknown, data: { content: string }) => callback(data)
    ipcRenderer.on('llm:stream-token', handler)
    return () => ipcRenderer.removeListener('llm:stream-token', handler)
  },
  onStreamDone: (callback: (data: { content: string; usage?: unknown; aborted?: boolean }) => void) => {
    const handler = (_event: unknown, data: { content: string; usage?: unknown; aborted?: boolean }) => callback(data)
    ipcRenderer.on('llm:stream-done', handler)
    return () => ipcRenderer.removeListener('llm:stream-done', handler)
  },
  onStreamError: (callback: (data: { error: string }) => void) => {
    const handler = (_event: unknown, data: { error: string }) => callback(data)
    ipcRenderer.on('llm:stream-error', handler)
    return () => ipcRenderer.removeListener('llm:stream-error', handler)
  }
}

// 配置 API
const configAPI = {
  save: (config: unknown) => ipcRenderer.invoke('config:save', config),
  load: () => ipcRenderer.invoke('config:load')
}

// 对话历史 API
const conversationAPI = {
  save: (conversation: unknown) => ipcRenderer.invoke('conversation:save', conversation),
  list: () => ipcRenderer.invoke('conversation:list'),
  load: (conversationId: string) => ipcRenderer.invoke('conversation:load', conversationId),
  delete: (conversationId: string) => ipcRenderer.invoke('conversation:delete', conversationId)
}

// 自定义 API
const api = {
  file: fileAPI,
  diff: diffAPI,
  backup: backupAPI,
  dialog: dialogAPI,
  clipboard: clipboardAPI,
  llm: llmAPI,
  config: configAPI,
  conversation: conversationAPI
}

// 暴露 API 到渲染进程
if (process.contextIsolated) {
  try {
    contextBridge.exposeInMainWorld('electron', electronAPI)
    contextBridge.exposeInMainWorld('api', api)
  } catch (error) {
    console.error(error)
  }
} else {
  // @ts-ignore (define in dts)
  window.electron = electronAPI
  // @ts-ignore (define in dts)
  window.api = api
}

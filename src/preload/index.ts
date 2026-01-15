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

// 自定义 API
const api = {
  file: fileAPI,
  diff: diffAPI,
  backup: backupAPI,
  dialog: dialogAPI,
  clipboard: clipboardAPI
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

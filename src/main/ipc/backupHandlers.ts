import { ipcMain } from 'electron'
import * as fs from 'fs'
import * as path from 'path'

export interface BackupInfo {
  path: string
  timestamp: string
  files: string[]
}

export function registerBackupHandlers(): void {
  // 获取备份列表
  ipcMain.handle('backup:list', async (_event, projectRoot: string) => {
    try {
      const backupDir = path.join(projectRoot, '.diff_backups')
      
      if (!fs.existsSync(backupDir)) {
        return { success: true, data: [] }
      }

      const entries = await fs.promises.readdir(backupDir, { withFileTypes: true })
      const backups: BackupInfo[] = []

      for (const entry of entries) {
        if (entry.isDirectory()) {
          const backupPath = path.join(backupDir, entry.name)
          const files = await fs.promises.readdir(backupPath)
          
          backups.push({
            path: backupPath,
            timestamp: entry.name,
            files
          })
        }
      }

      // 按时间戳倒序排列
      backups.sort((a, b) => b.timestamp.localeCompare(a.timestamp))

      return { success: true, data: backups }
    } catch (error) {
      return { success: false, error: String(error) }
    }
  })

  // 回滚备份
  ipcMain.handle('backup:rollback', async (_event, backupPath: string, projectRoot: string) => {
    try {
      if (!fs.existsSync(backupPath)) {
        return { success: false, error: '备份目录不存在' }
      }

      const files = await fs.promises.readdir(backupPath)
      let restoredCount = 0
      const errors: string[] = []

      for (const file of files) {
        try {
          const backupFilePath = path.join(backupPath, file)
          const targetPath = path.join(projectRoot, file)
          
          const content = await fs.promises.readFile(backupFilePath, 'utf-8')
          await fs.promises.writeFile(targetPath, content, 'utf-8')
          
          restoredCount++
        } catch (e) {
          errors.push(`${file}: ${String(e)}`)
        }
      }

      return {
        success: errors.length === 0,
        restoredCount,
        errors
      }
    } catch (error) {
      return { success: false, error: String(error) }
    }
  })

  // 删除备份
  ipcMain.handle('backup:delete', async (_event, backupPath: string) => {
    try {
      if (!fs.existsSync(backupPath)) {
        return { success: false, error: '备份目录不存在' }
      }

      await fs.promises.rm(backupPath, { recursive: true, force: true })
      return { success: true }
    } catch (error) {
      return { success: false, error: String(error) }
    }
  })

  // 创建手动备份
  ipcMain.handle('backup:create', async (_event, filePaths: string[], projectRoot: string) => {
    try {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)
      const backupDir = path.join(projectRoot, '.diff_backups', `manual_${timestamp}`)
      
      await fs.promises.mkdir(backupDir, { recursive: true })

      let backedUpCount = 0
      const errors: string[] = []

      for (const filePath of filePaths) {
        try {
          if (fs.existsSync(filePath)) {
            const content = await fs.promises.readFile(filePath, 'utf-8')
            const backupPath = path.join(backupDir, path.basename(filePath))
            await fs.promises.writeFile(backupPath, content, 'utf-8')
            backedUpCount++
          }
        } catch (e) {
          errors.push(`${filePath}: ${String(e)}`)
        }
      }

      return {
        success: errors.length === 0,
        backupDir,
        backedUpCount,
        errors
      }
    } catch (error) {
      return { success: false, error: String(error) }
    }
  })
}

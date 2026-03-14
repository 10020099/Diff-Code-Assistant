import { ipcMain } from 'electron'
import * as fs from 'fs'
import * as path from 'path'

export interface RollbackRecord {
  id: string
  timestamp: string
  fileCount: number
}

export function registerBackupHandlers(): void {
  // 获取回滚记录列表
  ipcMain.handle('backup:list', async (_event, projectRoot: string) => {
    try {
      const backupDir = path.join(projectRoot, '.diff_backups')

      if (!fs.existsSync(backupDir)) {
        return { success: true, data: [] }
      }

      const files = await fs.promises.readdir(backupDir)
      const records: RollbackRecord[] = []

      for (const file of files) {
        const match = file.match(/^rollback_(\d{8}-\d{6})\.json$/)
        if (!match) continue

        try {
          const content = await fs.promises.readFile(path.join(backupDir, file), 'utf-8')
          const data = JSON.parse(content)
          const fileCount = Object.keys(data.files || {}).length + (data.newFiles || []).length

          records.push({
            id: file.replace('.json', ''),
            timestamp: match[1],
            fileCount
          })
        } catch {
          // 忽略
        }
      }

      // 最新在前
      records.sort((a, b) => b.timestamp.localeCompare(a.timestamp))

      return { success: true, data: records }
    } catch (error) {
      return { success: false, error: String(error) }
    }
  })

  // 回滚（委托给 diff:rollback）
  ipcMain.handle('backup:rollback', async (_event, rollbackId: string, projectRoot: string) => {
    try {
      if (!/^rollback_\d{8}-\d{6}$/.test(rollbackId)) {
        return { success: false, error: '非法的回滚记录 ID' }
      }

      const backupDir = path.join(projectRoot, '.diff_backups')
      const filePath = path.join(backupDir, `${rollbackId}.json`)

      if (!fs.existsSync(filePath)) {
        return { success: false, error: '回滚记录不存在' }
      }

      const record = JSON.parse(await fs.promises.readFile(filePath, 'utf-8'))
      let restoredCount = 0
      const errors: string[] = []

      // 恢复修改过的文件
      for (const [relativePath, originalContent] of Object.entries(record.files || {})) {
        try {
          const targetPath = path.join(projectRoot, relativePath)
          await fs.promises.mkdir(path.dirname(targetPath), { recursive: true })
          await fs.promises.writeFile(targetPath, originalContent as string, 'utf-8')
          restoredCount++
        } catch (e) {
          errors.push(`${relativePath}: ${String(e)}`)
        }
      }

      // 删除新创建的文件
      for (const relativePath of (record.newFiles || [])) {
        try {
          const targetPath = path.join(projectRoot, relativePath)
          if (fs.existsSync(targetPath)) {
            await fs.promises.unlink(targetPath)
            restoredCount++
          }
        } catch (e) {
          errors.push(`删除 ${relativePath}: ${String(e)}`)
        }
      }

      return { success: errors.length === 0, restoredCount, errors }
    } catch (error) {
      return { success: false, error: String(error) }
    }
  })

  // 删除回滚记录
  ipcMain.handle('backup:delete', async (_event, rollbackId: string, projectRoot: string) => {
    try {
      if (!/^rollback_\d{8}-\d{6}$/.test(rollbackId)) {
        return { success: false, error: '非法的回滚记录 ID' }
      }

      const backupDir = path.join(projectRoot, '.diff_backups')
      const filePath = path.join(backupDir, `${rollbackId}.json`)

      if (fs.existsSync(filePath)) {
        await fs.promises.unlink(filePath)
      }
      return { success: true }
    } catch (error) {
      return { success: false, error: String(error) }
    }
  })

  // 手动创建回滚记录
  ipcMain.handle('backup:create', async (_event, filePaths: string[], projectRoot: string) => {
    try {
      const backupDir = path.join(projectRoot, '.diff_backups')
      await fs.promises.mkdir(backupDir, { recursive: true })

      const now = new Date()
      const y = now.getFullYear()
      const m = String(now.getMonth() + 1).padStart(2, '0')
      const d = String(now.getDate()).padStart(2, '0')
      const h = String(now.getHours()).padStart(2, '0')
      const min = String(now.getMinutes()).padStart(2, '0')
      const s = String(now.getSeconds()).padStart(2, '0')
      const timestamp = `${y}${m}${d}-${h}${min}${s}`

      const files: Record<string, string> = {}

      for (const filePath of filePaths) {
        try {
          if (fs.existsSync(filePath)) {
            const relativePath = path.relative(projectRoot, filePath)
            const content = await fs.promises.readFile(filePath, 'utf-8')
            files[relativePath] = content
          }
        } catch {
          // 忽略读取失败的文件
        }
      }

      const rollbackId = `rollback_${timestamp}`
      await fs.promises.writeFile(
        path.join(backupDir, `${rollbackId}.json`),
        JSON.stringify({ timestamp, files, newFiles: [] }, null, 2),
        'utf-8'
      )

      return { success: true, rollbackId, backedUpCount: Object.keys(files).length }
    } catch (error) {
      return { success: false, error: String(error) }
    }
  })
}

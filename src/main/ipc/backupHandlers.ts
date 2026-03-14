import { ipcMain } from 'electron'
import * as fs from 'fs'
import * as path from 'path'

export interface BackupFileInfo {
  backupName: string       // 备份文件名
  originalPath: string     // 原始相对路径
  timestamp: string        // 时间戳
  sizeBytes: number
}

/**
 * 生成备份文件名：将相对路径中的分隔符替换为 __，后缀加时间戳
 * 例如: src/utils/foo.ts → src__utils__foo.ts.20260315-003000.bak
 */
function toBackupName(relativePath: string, timestamp: string): string {
  const flattened = relativePath.replace(/[\\/]/g, '__')
  return `${flattened}.${timestamp}.bak`
}

/**
 * 从备份文件名解析出原始相对路径和时间戳
 */
function parseBackupName(backupName: string): { originalPath: string; timestamp: string } | null {
  // 匹配 xxx.YYYYMMDD-HHMMSS.bak
  const match = backupName.match(/^(.+)\.(\d{8}-\d{6})\.bak$/)
  if (!match) return null

  const flattened = match[1]
  const timestamp = match[2]
  // 把 __ 还原为路径分隔符
  const originalPath = flattened.replace(/__/g, path.sep)

  return { originalPath, timestamp }
}

/**
 * 生成时间戳字符串: YYYYMMDD-HHMMSS
 */
function makeTimestamp(): string {
  const now = new Date()
  const y = now.getFullYear()
  const m = String(now.getMonth() + 1).padStart(2, '0')
  const d = String(now.getDate()).padStart(2, '0')
  const h = String(now.getHours()).padStart(2, '0')
  const min = String(now.getMinutes()).padStart(2, '0')
  const s = String(now.getSeconds()).padStart(2, '0')
  return `${y}${m}${d}-${h}${min}${s}`
}

function getBackupDir(projectRoot: string): string {
  return path.join(projectRoot, '.diff_backups')
}

/**
 * 自动清理：每个原始文件只保留最近 maxPerFile 份备份
 */
async function autoCleanBackups(backupDir: string, maxPerFile: number = 5): Promise<void> {
  if (!fs.existsSync(backupDir)) return

  const files = await fs.promises.readdir(backupDir)

  // 按原始路径分组
  const groups = new Map<string, { name: string; timestamp: string }[]>()

  for (const file of files) {
    const parsed = parseBackupName(file)
    if (!parsed) continue

    if (!groups.has(parsed.originalPath)) {
      groups.set(parsed.originalPath, [])
    }
    groups.get(parsed.originalPath)!.push({ name: file, timestamp: parsed.timestamp })
  }

  // 每组只保留最近 maxPerFile 份
  for (const [, backups] of groups) {
    if (backups.length <= maxPerFile) continue

    // 按时间戳降序排序，保留前 maxPerFile 个
    backups.sort((a, b) => b.timestamp.localeCompare(a.timestamp))
    const toDelete = backups.slice(maxPerFile)

    for (const backup of toDelete) {
      try {
        await fs.promises.unlink(path.join(backupDir, backup.name))
      } catch {
        // 忽略
      }
    }
  }
}

export function registerBackupHandlers(): void {
  // 获取备份列表
  ipcMain.handle('backup:list', async (_event, projectRoot: string) => {
    try {
      const backupDir = getBackupDir(projectRoot)

      if (!fs.existsSync(backupDir)) {
        return { success: true, data: [] }
      }

      const files = await fs.promises.readdir(backupDir)
      const backups: BackupFileInfo[] = []

      for (const file of files) {
        const parsed = parseBackupName(file)
        if (!parsed) continue

        try {
          const stat = await fs.promises.stat(path.join(backupDir, file))
          backups.push({
            backupName: file,
            originalPath: parsed.originalPath,
            timestamp: parsed.timestamp,
            sizeBytes: stat.size
          })
        } catch {
          // 忽略
        }
      }

      // 按时间戳倒序
      backups.sort((a, b) => b.timestamp.localeCompare(a.timestamp))

      return { success: true, data: backups }
    } catch (error) {
      return { success: false, error: String(error) }
    }
  })

  // 回滚：将备份文件还原到原始位置
  ipcMain.handle('backup:rollback', async (_event, backupName: string, projectRoot: string) => {
    try {
      const backupDir = getBackupDir(projectRoot)
      const backupFilePath = path.join(backupDir, backupName)

      if (!fs.existsSync(backupFilePath)) {
        return { success: false, error: '备份文件不存在' }
      }

      const parsed = parseBackupName(backupName)
      if (!parsed) {
        return { success: false, error: '无法解析备份文件名' }
      }

      const targetPath = path.join(projectRoot, parsed.originalPath)

      // 确保目标目录存在
      await fs.promises.mkdir(path.dirname(targetPath), { recursive: true })

      const content = await fs.promises.readFile(backupFilePath)
      await fs.promises.writeFile(targetPath, content)

      return { success: true, restoredPath: parsed.originalPath }
    } catch (error) {
      return { success: false, error: String(error) }
    }
  })

  // 删除备份
  ipcMain.handle('backup:delete', async (_event, backupName: string, projectRoot: string) => {
    try {
      const backupDir = getBackupDir(projectRoot)
      const backupFilePath = path.join(backupDir, backupName)

      if (fs.existsSync(backupFilePath)) {
        await fs.promises.unlink(backupFilePath)
      }
      return { success: true }
    } catch (error) {
      return { success: false, error: String(error) }
    }
  })

  // 创建备份（由 diffHandlers 调用，也支持手动）
  ipcMain.handle('backup:create', async (_event, filePaths: string[], projectRoot: string) => {
    try {
      const backupDir = getBackupDir(projectRoot)
      await fs.promises.mkdir(backupDir, { recursive: true })

      const timestamp = makeTimestamp()
      let backedUpCount = 0
      const errors: string[] = []

      for (const filePath of filePaths) {
        try {
          if (fs.existsSync(filePath)) {
            const relativePath = path.relative(projectRoot, filePath)
            const backupName = toBackupName(relativePath, timestamp)
            const backupFilePath = path.join(backupDir, backupName)

            const content = await fs.promises.readFile(filePath)
            await fs.promises.writeFile(backupFilePath, content)
            backedUpCount++
          }
        } catch (e) {
          errors.push(`${filePath}: ${String(e)}`)
        }
      }

      // 自动清理：每个文件只保留最近5份
      await autoCleanBackups(backupDir)

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

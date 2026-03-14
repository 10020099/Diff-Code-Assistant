import { ipcMain } from 'electron'
import * as fs from 'fs'
import * as path from 'path'
import {
  parseDiff,
  validateDiff,
  applyDiffToContent,
  cleanFilePath
} from '../utils/diffParser'

export interface ApplyDiffResult {
  success: boolean
  successCount: number
  errorCount: number
  errors: string[]
  backupDir?: string
}

export function registerDiffHandlers(): void {
  // 验证 diff
  ipcMain.handle('diff:validate', (_event, diffContent: string) => {
    return validateDiff(diffContent)
  })

  // 解析 diff
  ipcMain.handle('diff:parse', (_event, diffContent: string) => {
    try {
      const fileChanges = parseDiff(diffContent)
      return { success: true, data: fileChanges }
    } catch (error) {
      return { success: false, error: String(error) }
    }
  })

  // 应用 diff
  ipcMain.handle('diff:apply', async (_event, diffContent: string, projectRoot: string, options?: {
    createBackup?: boolean
    dryRun?: boolean
  }) => {
    const createBackup = options?.createBackup ?? true
    const dryRun = options?.dryRun ?? false

    const result: ApplyDiffResult = {
      success: true,
      successCount: 0,
      errorCount: 0,
      errors: []
    }

    try {
      // 验证 diff
      const validation = validateDiff(diffContent)
      if (!validation.isValid) {
        result.success = false
        return {
          error: validation.message,
          ...result
        }
      }

      // 解析 diff
      const fileChanges = parseDiff(diffContent)
      if (fileChanges.length === 0) {
        result.success = false
        return {
          error: '无法解析Diff内容或没有发现文件修改',
          ...result
        }
      }

      // 准备备份
      const backupDir = path.join(projectRoot, '.diff_backups')
      const timestamp = (() => {
        const now = new Date()
        const y = now.getFullYear()
        const m = String(now.getMonth() + 1).padStart(2, '0')
        const d = String(now.getDate()).padStart(2, '0')
        const h = String(now.getHours()).padStart(2, '0')
        const min = String(now.getMinutes()).padStart(2, '0')
        const s = String(now.getSeconds()).padStart(2, '0')
        return `${y}${m}${d}-${h}${min}${s}`
      })()

      if (createBackup && !dryRun) {
        await fs.promises.mkdir(backupDir, { recursive: true })
        result.backupDir = backupDir
      }

      // 应用每个文件的修改
      for (const fileChange of fileChanges) {
        try {
          const cleanPath = cleanFilePath(fileChange.newPath)
          const fullPath = path.isAbsolute(cleanPath)
            ? path.join(projectRoot, path.basename(cleanPath))
            : path.join(projectRoot, cleanPath)

          // 读取原文件内容
          let originalContent = ''
          if (fs.existsSync(fullPath)) {
            originalContent = await fs.promises.readFile(fullPath, 'utf-8')

            // 创建备份（文件名带时间戳，放在同一个文件夹）
            if (createBackup && !dryRun) {
              const relativePath = path.relative(projectRoot, fullPath)
              const flatName = relativePath.replace(/[\\/]/g, '__')
              const backupFileName = `${flatName}.${timestamp}.bak`
              await fs.promises.writeFile(
                path.join(backupDir, backupFileName),
                originalContent,
                'utf-8'
              )
            }
          }

          // 应用 diff
          const newContent = applyDiffToContent(originalContent, fileChange)

          // 写入文件（非预览模式）
          if (!dryRun) {
            await fs.promises.mkdir(path.dirname(fullPath), { recursive: true })
            await fs.promises.writeFile(fullPath, newContent, 'utf-8')
          }

          result.successCount++
        } catch (error) {
          result.errorCount++
          result.errors.push(`${fileChange.newPath}: ${String(error)}`)
        }
      }

      // 自动清理：每个原始文件只保留最近5份备份
      if (createBackup && !dryRun) {
        try {
          const allFiles = await fs.promises.readdir(backupDir)
          const groups = new Map<string, { name: string; ts: string }[]>()

          for (const file of allFiles) {
            const match = file.match(/^(.+)\.(\d{8}-\d{6})\.bak$/)
            if (!match) continue
            const key = match[1] // 扁平化的原始路径
            if (!groups.has(key)) groups.set(key, [])
            groups.get(key)!.push({ name: file, ts: match[2] })
          }

          for (const [, backups] of groups) {
            if (backups.length <= 5) continue
            backups.sort((a, b) => b.ts.localeCompare(a.ts))
            for (const old of backups.slice(5)) {
              await fs.promises.unlink(path.join(backupDir, old.name)).catch(() => { })
            }
          }
        } catch {
          // 清理失败不影响主流程
        }
      }

      result.success = result.errorCount === 0
      return result
    } catch (error) {
      return {
        error: String(error),
        ...result,
        success: false
      }
    }
  })

  // 检查文件冲突
  ipcMain.handle('diff:checkConflicts', async (_event, diffContent: string, projectRoot: string) => {
    const conflicts: string[] = []

    try {
      const fileChanges = parseDiff(diffContent)

      for (const change of fileChanges) {
        const cleanPath = cleanFilePath(change.newPath)
        const fullPath = path.isAbsolute(cleanPath)
          ? path.join(projectRoot, path.basename(cleanPath))
          : path.join(projectRoot, cleanPath)

        if (fs.existsSync(fullPath)) {
          try {
            await fs.promises.access(fullPath, fs.constants.W_OK)
          } catch {
            conflicts.push(`${change.newPath}: 文件只读，无法修改`)
          }
        } else {
          const dirPath = path.dirname(fullPath)
          if (dirPath && !fs.existsSync(dirPath)) {
            try {
              await fs.promises.mkdir(dirPath, { recursive: true })
            } catch (e) {
              conflicts.push(`${change.newPath}: 无法创建目录 - ${e}`)
            }
          }
        }
      }

      return { success: true, conflicts }
    } catch (error) {
      return { success: false, error: String(error), conflicts }
    }
  })
}

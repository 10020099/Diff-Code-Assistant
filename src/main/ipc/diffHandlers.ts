import { ipcMain } from 'electron'
import * as fs from 'fs'
import * as path from 'path'
import { 
  parseDiff, 
  validateDiff, 
  applyDiffToContent,
  cleanFilePath,
  FileChange 
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
        return {
          success: false,
          error: validation.message,
          ...result
        }
      }

      // 解析 diff
      const fileChanges = parseDiff(diffContent)
      if (fileChanges.length === 0) {
        return {
          success: false,
          error: '无法解析Diff内容或没有发现文件修改',
          ...result
        }
      }

      // 创建备份目录
      let backupDir: string | undefined
      if (createBackup && !dryRun) {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)
        backupDir = path.join(projectRoot, '.diff_backups', timestamp)
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
            
            // 创建备份
            if (createBackup && !dryRun && backupDir) {
              const backupPath = path.join(backupDir, path.basename(fullPath))
              await fs.promises.writeFile(backupPath, originalContent, 'utf-8')
            }
          }

          // 应用 diff
          const newContent = applyDiffToContent(originalContent, fileChange)

          // 写入文件（非预览模式）
          if (!dryRun) {
            // 确保目录存在
            await fs.promises.mkdir(path.dirname(fullPath), { recursive: true })
            await fs.promises.writeFile(fullPath, newContent, 'utf-8')
          }

          result.successCount++
        } catch (error) {
          result.errorCount++
          result.errors.push(`${fileChange.newPath}: ${String(error)}`)
        }
      }

      result.success = result.errorCount === 0
      return result
    } catch (error) {
      return {
        success: false,
        error: String(error),
        ...result
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

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
  rollbackId?: string
}

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

  // 应用 diff（原子性：全部成功才写入，失败自动回滚）
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
        return { error: validation.message, ...result }
      }

      // 解析 diff
      const fileChanges = parseDiff(diffContent)
      if (fileChanges.length === 0) {
        result.success = false
        return { error: '无法解析Diff内容或没有发现文件修改', ...result }
      }

      // ===== 阶段 1：在内存中计算所有修改，不写磁盘 =====
      const operations: Array<{
        fullPath: string
        relativePath: string
        originalContent: string
        newContent: string
        isNewFile: boolean
      }> = []

      for (const fileChange of fileChanges) {
        const cleanPath = cleanFilePath(fileChange.newPath)
        const fullPath = path.isAbsolute(cleanPath)
          ? path.join(projectRoot, path.basename(cleanPath))
          : path.join(projectRoot, cleanPath)

        let originalContent = ''
        let isNewFile = true

        if (fs.existsSync(fullPath)) {
          originalContent = await fs.promises.readFile(fullPath, 'utf-8')
          isNewFile = false
        }

        // 在内存中应用 diff（如果这一步出错，还没写任何文件）
        const newContent = applyDiffToContent(originalContent, fileChange)

        operations.push({
          fullPath,
          relativePath: path.relative(projectRoot, fullPath),
          originalContent,
          newContent,
          isNewFile
        })
      }

      // 预览模式到此为止
      if (dryRun) {
        result.successCount = operations.length
        return result
      }

      // ===== 阶段 2：保存回滚记录 =====
      const timestamp = makeTimestamp()

      if (createBackup) {
        const backupDir = path.join(projectRoot, '.diff_backups')
        await fs.promises.mkdir(backupDir, { recursive: true })

        const rollbackRecord = {
          timestamp,
          files: Object.fromEntries(
            operations
              .filter(op => !op.isNewFile) // 新文件无需记录原始内容
              .map(op => [op.relativePath, op.originalContent])
          ),
          newFiles: operations
            .filter(op => op.isNewFile)
            .map(op => op.relativePath)
        }

        const rollbackId = `rollback_${timestamp}`
        await fs.promises.writeFile(
          path.join(backupDir, `${rollbackId}.json`),
          JSON.stringify(rollbackRecord, null, 2),
          'utf-8'
        )
        result.rollbackId = rollbackId

        // 自动清理：只保留最近 20 条回滚记录
        try {
          const allFiles = await fs.promises.readdir(backupDir)
          const rollbacks = allFiles
            .filter(f => f.startsWith('rollback_') && f.endsWith('.json'))
            .sort()

          if (rollbacks.length > 20) {
            for (const old of rollbacks.slice(0, rollbacks.length - 20)) {
              await fs.promises.unlink(path.join(backupDir, old)).catch(() => { })
            }
          }
        } catch {
          // 清理失败不影响主流程
        }
      }

      // ===== 阶段 3：原子写入所有文件，失败则回滚 =====
      const written: string[] = []

      try {
        for (const op of operations) {
          await fs.promises.mkdir(path.dirname(op.fullPath), { recursive: true })
          await fs.promises.writeFile(op.fullPath, op.newContent, 'utf-8')
          written.push(op.fullPath)
          result.successCount++
        }
      } catch (writeError) {
        // 写入中途失败 → 回滚所有已写入的文件
        for (const op of operations) {
          if (written.includes(op.fullPath)) {
            try {
              if (op.isNewFile) {
                // 新创建的文件：删除
                await fs.promises.unlink(op.fullPath).catch(() => { })
              } else {
                // 已有文件：恢复原始内容
                await fs.promises.writeFile(op.fullPath, op.originalContent, 'utf-8')
              }
            } catch {
              // 回滚失败只记录，不再抛
            }
          }
        }

        result.success = false
        result.errorCount = fileChanges.length - written.length
        result.errors.push(`写入失败并已回滚: ${String(writeError)}`)
        return result
      }

      result.success = true
      return result
    } catch (error) {
      return { error: String(error), ...result, success: false }
    }
  })

  // 列出回滚记录
  ipcMain.handle('diff:listRollbacks', async (_event, projectRoot: string) => {
    try {
      const backupDir = path.join(projectRoot, '.diff_backups')
      if (!fs.existsSync(backupDir)) return { success: true, data: [] }

      const allFiles = await fs.promises.readdir(backupDir)
      const rollbacks = allFiles
        .filter(f => f.startsWith('rollback_') && f.endsWith('.json'))
        .sort()
        .reverse() // 最新在前
        .map(f => {
          const match = f.match(/^rollback_(\d{8}-\d{6})\.json$/)
          return { id: f.replace('.json', ''), timestamp: match?.[1] || '', fileName: f }
        })

      return { success: true, data: rollbacks }
    } catch (error) {
      return { success: false, error: String(error) }
    }
  })

  // 执行回滚
  ipcMain.handle('diff:rollback', async (_event, rollbackId: string, projectRoot: string) => {
    try {
      // 校验 ID 安全性
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
      for (const [relativePath, originalContent] of Object.entries(record.files)) {
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
      if (record.newFiles) {
        for (const relativePath of record.newFiles) {
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
      }

      return { success: errors.length === 0, restoredCount, errors }
    } catch (error) {
      return { success: false, error: String(error) }
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
        }
      }

      return { success: true, conflicts }
    } catch (error) {
      return { success: false, error: String(error), conflicts }
    }
  })
}

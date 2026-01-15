import { ipcMain } from 'electron'
import { 
  scanDirectory, 
  generateContext, 
  DEFAULT_EXCLUDE_PATTERNS,
  SUPPORTED_EXTENSIONS,
  FileInfo 
} from '../utils/fileScanner'

export function registerFileHandlers(): void {
  // 扫描目录
  ipcMain.handle('file:scan', async (_event, rootDir: string, options?: {
    excludePatterns?: string[]
    maxFileSize?: number
  }) => {
    try {
      const excludePatterns = options?.excludePatterns || DEFAULT_EXCLUDE_PATTERNS
      const maxFileSize = options?.maxFileSize || 1024 * 1024
      
      const result = await scanDirectory(rootDir, excludePatterns, maxFileSize)
      return { success: true, data: result }
    } catch (error) {
      return { success: false, error: String(error) }
    }
  })

  // 生成上下文
  ipcMain.handle('file:generateContext', async (_event, files: FileInfo[], rootDir: string, includeLineNumbers: boolean = true) => {
    try {
      const context = await generateContext(files, rootDir, includeLineNumbers)
      return { success: true, data: context }
    } catch (error) {
      return { success: false, error: String(error) }
    }
  })

  // 获取默认排除模式
  ipcMain.handle('file:getDefaultExcludePatterns', () => {
    return DEFAULT_EXCLUDE_PATTERNS
  })

  // 获取支持的文件扩展名
  ipcMain.handle('file:getSupportedExtensions', () => {
    return SUPPORTED_EXTENSIONS
  })
}

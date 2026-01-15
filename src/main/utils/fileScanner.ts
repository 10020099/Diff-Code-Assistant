import * as fs from 'fs'
import * as path from 'path'
import { glob } from 'glob'

// 默认排除模式
export const DEFAULT_EXCLUDE_PATTERNS = [
  '*.pyc', '__pycache__', '.git', '.gitignore', 'node_modules',
  '.vscode', '.idea', '*.log', '.env', 'dist', 'build',
  '*.egg-info', '.pytest_cache', '.coverage', '*.tmp', '*.bak',
  '.DS_Store', 'Thumbs.db', '*.lock', 'package-lock.json', 'yarn.lock'
]

// 支持的文件扩展名
export const SUPPORTED_EXTENSIONS: Record<string, string> = {
  '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript', '.jsx': 'React JSX',
  '.tsx': 'React TSX', '.java': 'Java', '.cpp': 'C++', '.c': 'C', '.h': 'Header',
  '.cs': 'C#', '.php': 'PHP', '.rb': 'Ruby', '.go': 'Go', '.rs': 'Rust',
  '.swift': 'Swift', '.kt': 'Kotlin', '.html': 'HTML', '.css': 'CSS',
  '.scss': 'SCSS', '.xml': 'XML', '.json': 'JSON', '.yaml': 'YAML',
  '.yml': 'YAML', '.md': 'Markdown', '.txt': 'Text', '.sql': 'SQL',
  '.sh': 'Shell', '.bat': 'Batch', '.ps1': 'PowerShell', '.vue': 'Vue'
}

export interface FileInfo {
  path: string
  relativePath: string
  name: string
  extension: string
  size: number
  sizeStr: string
  type: string
  isText: boolean
}

export interface ScanResult {
  files: FileInfo[]
  totalFiles: number
  totalSize: number
  totalLines: number
  fileTypes: Record<string, number>
}

/**
 * 检查文件是否为文本文件
 */
export function isTextFile(filePath: string): boolean {
  try {
    const buffer = Buffer.alloc(512)
    const fd = fs.openSync(filePath, 'r')
    const bytesRead = fs.readSync(fd, buffer, 0, 512, 0)
    fs.closeSync(fd)

    // 检查是否包含 null 字节（二进制文件的特征）
    for (let i = 0; i < bytesRead; i++) {
      if (buffer[i] === 0) {
        return false
      }
    }
    return true
  } catch {
    return false
  }
}

/**
 * 获取文件大小的字符串表示
 */
export function getFileSizeStr(size: number): string {
  if (size < 1024) {
    return `${size} B`
  } else if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(1)} KB`
  } else {
    return `${(size / (1024 * 1024)).toFixed(1)} MB`
  }
}

/**
 * 检查路径是否匹配排除模式
 */
function matchesExcludePattern(relativePath: string, patterns: string[]): boolean {
  const normalizedPath = relativePath.replace(/\\/g, '/')
  const parts = normalizedPath.split('/')
  
  for (const pattern of patterns) {
    // 检查完整路径
    if (minimatch(normalizedPath, pattern)) {
      return true
    }
    // 检查每个路径部分
    for (const part of parts) {
      if (minimatch(part, pattern)) {
        return true
      }
    }
  }
  return false
}

/**
 * 简单的 glob 匹配函数
 */
function minimatch(str: string, pattern: string): boolean {
  // 转换 glob 模式为正则表达式
  const regexPattern = pattern
    .replace(/\./g, '\\.')
    .replace(/\*/g, '.*')
    .replace(/\?/g, '.')
  
  const regex = new RegExp(`^${regexPattern}$`, 'i')
  return regex.test(str)
}

/**
 * 扫描目录
 */
export async function scanDirectory(
  rootDir: string,
  excludePatterns: string[] = DEFAULT_EXCLUDE_PATTERNS,
  maxFileSize: number = 1024 * 1024
): Promise<ScanResult> {
  const files: FileInfo[] = []
  let totalSize = 0
  let totalLines = 0
  const fileTypes: Record<string, number> = {}

  async function walkDir(dir: string): Promise<void> {
    const entries = await fs.promises.readdir(dir, { withFileTypes: true })

    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name)
      const relativePath = path.relative(rootDir, fullPath)

      // 检查是否匹配排除模式
      if (matchesExcludePattern(relativePath, excludePatterns)) {
        continue
      }

      if (entry.isDirectory()) {
        await walkDir(fullPath)
      } else if (entry.isFile()) {
        try {
          const stats = await fs.promises.stat(fullPath)
          
          // 跳过过大的文件
          if (stats.size > maxFileSize) {
            continue
          }

          // 检查是否为文本文件
          if (!isTextFile(fullPath)) {
            continue
          }

          const ext = path.extname(entry.name).toLowerCase()
          const fileType = SUPPORTED_EXTENSIONS[ext] || 'Unknown'

          // 统计行数
          let lineCount = 0
          try {
            const content = await fs.promises.readFile(fullPath, 'utf-8')
            lineCount = content.split('\n').length
            totalLines += lineCount
          } catch {
            // 忽略读取错误
          }

          const fileInfo: FileInfo = {
            path: fullPath,
            relativePath,
            name: entry.name,
            extension: ext,
            size: stats.size,
            sizeStr: getFileSizeStr(stats.size),
            type: fileType,
            isText: true
          }

          files.push(fileInfo)
          totalSize += stats.size
          fileTypes[ext] = (fileTypes[ext] || 0) + 1
        } catch {
          // 忽略无法访问的文件
        }
      }
    }
  }

  await walkDir(rootDir)

  // 按相对路径排序
  files.sort((a, b) => a.relativePath.localeCompare(b.relativePath))

  return {
    files,
    totalFiles: files.length,
    totalSize,
    totalLines,
    fileTypes
  }
}

/**
 * 构建文件树字符串
 */
export function buildTree(files: FileInfo[], rootDir: string): string {
  if (files.length === 0) {
    return '空项目\n'
  }

  let tree = `项目: ${path.basename(rootDir)}\n`
  const sortedPaths = files.map(f => f.relativePath).sort()

  let prevParts: string[] = []
  for (const relPath of sortedPaths) {
    const parts = relPath.split(path.sep)
    for (let i = 0; i < parts.length; i++) {
      const part = parts[i]
      const prefix = '│   '.repeat(i) + '├── '
      
      if (prevParts.slice(0, i + 1).join('/') !== parts.slice(0, i + 1).join('/')) {
        if (i === parts.length - 1) {
          const file = files.find(f => f.relativePath === relPath)
          const sizeStr = file ? file.sizeStr : ''
          tree += `${prefix}${part} (${sizeStr})\n`
        } else {
          tree += `${prefix}${part}/\n`
        }
      }
    }
    prevParts = parts
  }

  return tree
}

/**
 * 生成上下文
 */
export async function generateContext(
  files: FileInfo[],
  rootDir: string,
  includeLineNumbers: boolean = true
): Promise<string> {
  if (files.length === 0) {
    return '没有选择任何文件。\n'
  }

  const treeStr = buildTree(files, rootDir)
  let context = `=== 项目结构 ===\n${treeStr}\n=== 文件内容 (${files.length} 个文件) ===\n\n`

  for (let i = 0; i < files.length; i++) {
    const file = files[i]
    try {
      let content = await fs.promises.readFile(file.path, 'utf-8')

      if (includeLineNumbers && content.trim()) {
        const lines = content.split('\n')
        const numberedLines = lines.map((line, idx) => 
          `${String(idx + 1).padStart(4)} | ${line}`
        )
        content = numberedLines.join('\n')
      }

      context += `--- 文件 ${i + 1}: ${file.relativePath} ---\n${content}\n--- 文件 ${i + 1} 结束 ---\n\n`
    } catch (e) {
      context += `--- 文件 ${i + 1}: ${file.relativePath} ---\n<读取失败: ${e}>\n--- 文件 ${i + 1} 结束 ---\n\n`
    }
  }

  return context
}

/**
 * 读取文件内容
 */
export async function readFileContent(filePath: string): Promise<string> {
  return fs.promises.readFile(filePath, 'utf-8')
}

/**
 * 写入文件内容
 */
export async function writeFileContent(filePath: string, content: string): Promise<void> {
  // 确保目录存在
  const dir = path.dirname(filePath)
  await fs.promises.mkdir(dir, { recursive: true })
  await fs.promises.writeFile(filePath, content, 'utf-8')
}

/**
 * Diff 解析器
 * 解析标准 unified diff 格式
 */

export interface DiffHunk {
  oldStart: number
  oldCount: number
  newStart: number
  newCount: number
  lines: string[]
}

export interface FileChange {
  oldPath: string
  newPath: string
  hunks: DiffHunk[]
  isNewFile: boolean
  isDeletedFile: boolean
}

export interface DiffValidationResult {
  isValid: boolean
  message: string
  warnings: string[]
  errors: string[]
}

/**
 * 验证 diff 内容
 */
export function validateDiff(diffContent: string): DiffValidationResult {
  const warnings: string[] = []
  const errors: string[] = []

  if (!diffContent.trim()) {
    return {
      isValid: false,
      message: 'Diff内容为空',
      warnings: [],
      errors: ['Diff内容为空']
    }
  }

  const lines = diffContent.trim().split('\n')

  const hasFileHeaders = lines.some(line => 
    line.startsWith('--- ') || line.startsWith('+++ ')
  )
  const hasHunkHeaders = lines.some(line => line.startsWith('@@'))
  const hasChanges = lines.some(line => 
    (line.startsWith('+') || line.startsWith('-')) && 
    !line.startsWith('+++') && !line.startsWith('---')
  )

  if (!hasFileHeaders) {
    warnings.push('缺少文件头信息 (--- 和 +++ 行)')
  }

  if (!hasHunkHeaders) {
    warnings.push('缺少hunk头信息 (@@ 行)')
  }

  if (!hasChanges) {
    errors.push('没有发现实际的代码更改')
  }

  // 验证 hunk 头格式
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    if (line.startsWith('@@')) {
      if (!/^@@ -\d+(?:,\d+)? \+\d+(?:,\d+)? @@/.test(line)) {
        errors.push(`第 ${i + 1} 行: hunk头格式不正确`)
      }
    }
  }

  // 提取文件路径
  const filePaths: string[] = []
  for (const line of lines) {
    if (line.startsWith('--- ') || line.startsWith('+++ ')) {
      let filePath = line.slice(4).trim()
      if (filePath.includes('\t')) {
        filePath = filePath.split('\t')[0].trim()
      }
      if (filePath.startsWith('a/')) {
        filePath = filePath.slice(2)
      } else if (filePath.startsWith('b/')) {
        filePath = filePath.slice(2)
      }
      if (filePath && filePath !== '/dev/null') {
        filePaths.push(filePath)
      }
    }
  }

  if (filePaths.length === 0) {
    errors.push('没有找到有效的文件路径')
  }

  const isValid = errors.length === 0
  let message = ''

  if (errors.length > 0) {
    message = '错误: ' + errors.join('; ')
  } else if (warnings.length > 0) {
    message = '警告: ' + warnings.join('; ')
  } else {
    message = '格式验证通过'
  }

  return { isValid, message, warnings, errors }
}

/**
 * 解析 diff 内容
 */
export function parseDiff(diffContent: string): FileChange[] {
  if (!diffContent.trim()) {
    return []
  }

  const lines = diffContent.trim().split('\n')
  const fileChanges: FileChange[] = []
  
  let currentFile: { oldPath: string; newPath: string } | null = null
  let currentHunks: DiffHunk[] = []
  let currentHunk: { oldStart: number; oldCount: number; newStart: number; newCount: number } | null = null
  let currentHunkLines: string[] = []

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]

    if (line.startsWith('--- ')) {
      // 保存之前的文件
      if (currentFile && currentHunks.length > 0) {
        if (currentHunk) {
          currentHunks.push({ ...currentHunk, lines: currentHunkLines })
        }
        fileChanges.push({
          oldPath: currentFile.oldPath,
          newPath: currentFile.newPath,
          hunks: currentHunks,
          isNewFile: currentFile.oldPath === '/dev/null',
          isDeletedFile: currentFile.newPath === '/dev/null'
        })
      }

      // 解析旧文件路径
      let oldPath = line.slice(4).trim()
      if (oldPath.includes('\t')) {
        oldPath = oldPath.split('\t')[0].trim()
      }
      if (oldPath.startsWith('a/')) {
        oldPath = oldPath.slice(2)
      }

      // 解析新文件路径
      let newPath = oldPath
      if (i + 1 < lines.length && lines[i + 1].startsWith('+++ ')) {
        newPath = lines[i + 1].slice(4).trim()
        if (newPath.includes('\t')) {
          newPath = newPath.split('\t')[0].trim()
        }
        if (newPath.startsWith('b/')) {
          newPath = newPath.slice(2)
        }
        i++ // 跳过 +++ 行
      }

      currentFile = { oldPath, newPath }
      currentHunks = []
      currentHunk = null
      currentHunkLines = []
    } else if (line.startsWith('@@')) {
      // 保存之前的 hunk
      if (currentHunk) {
        currentHunks.push({ ...currentHunk, lines: currentHunkLines })
      }

      // 解析 hunk 头
      const match = line.match(/@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@/)
      if (match) {
        currentHunk = {
          oldStart: parseInt(match[1], 10),
          oldCount: parseInt(match[2] || '1', 10),
          newStart: parseInt(match[3], 10),
          newCount: parseInt(match[4] || '1', 10)
        }
        currentHunkLines = []
      }
    } else if (currentHunk && line.length > 0 && [' ', '+', '-'].includes(line[0])) {
      currentHunkLines.push(line)
    }
  }

  // 保存最后一个文件
  if (currentFile && currentHunks.length > 0) {
    if (currentHunk) {
      currentHunks.push({ ...currentHunk, lines: currentHunkLines })
    }
    fileChanges.push({
      oldPath: currentFile.oldPath,
      newPath: currentFile.newPath,
      hunks: currentHunks,
      isNewFile: currentFile.oldPath === '/dev/null',
      isDeletedFile: currentFile.newPath === '/dev/null'
    })
  } else if (currentFile && currentHunk) {
    // 只有一个 hunk 的情况
    currentHunks.push({ ...currentHunk, lines: currentHunkLines })
    fileChanges.push({
      oldPath: currentFile.oldPath,
      newPath: currentFile.newPath,
      hunks: currentHunks,
      isNewFile: currentFile.oldPath === '/dev/null',
      isDeletedFile: currentFile.newPath === '/dev/null'
    })
  }

  return fileChanges
}

/**
 * 将 hunk 应用到文件行
 */
export function applyHunkToLines(lines: string[], hunk: DiffHunk): string[] {
  const result = [...lines]
  const startLine = hunk.oldStart - 1
  
  // 收集要删除和添加的行
  const toDelete: Array<{ lineIdx: number; content: string }> = []
  const toAdd: Array<{ lineIdx: number; content: string }> = []
  let currentLine = startLine

  for (const line of hunk.lines) {
    if (line.startsWith(' ')) {
      currentLine++
    } else if (line.startsWith('-')) {
      toDelete.push({ lineIdx: currentLine, content: line.slice(1) })
      currentLine++
    } else if (line.startsWith('+')) {
      toAdd.push({ lineIdx: currentLine, content: line.slice(1) })
    }
  }

  // 从后往前删除行
  for (const { lineIdx, content } of toDelete.reverse()) {
    if (lineIdx < result.length) {
      if (result[lineIdx].trimEnd() === content.trimEnd()) {
        result.splice(lineIdx, 1)
      } else {
        console.warn(`要删除的行内容不匹配在行 ${lineIdx + 1}`)
      }
    }
  }

  // 添加新行
  currentLine = startLine
  let insertOffset = 0

  for (const line of hunk.lines) {
    if (line.startsWith(' ')) {
      currentLine++
    } else if (line.startsWith('-')) {
      insertOffset--
      currentLine++
    } else if (line.startsWith('+')) {
      const addContent = line.slice(1)
      const insertPos = currentLine + insertOffset
      if (insertPos <= result.length) {
        result.splice(insertPos, 0, addContent)
        insertOffset++
      } else {
        result.push(addContent)
        insertOffset++
      }
    }
  }

  return result
}

/**
 * 将 diff 应用到文件
 */
export function applyDiffToContent(content: string, fileChange: FileChange): string {
  let lines = content.split('\n')
  
  // 从后往前应用 hunks，避免行号偏移问题
  const sortedHunks = [...fileChange.hunks].sort((a, b) => b.oldStart - a.oldStart)
  
  for (const hunk of sortedHunks) {
    lines = applyHunkToLines(lines, hunk)
  }

  return lines.join('\n')
}

/**
 * 清理文件路径
 */
export function cleanFilePath(filePath: string): string {
  let cleanPath = filePath

  // 移除时间戳
  if (cleanPath.includes('\t')) {
    cleanPath = cleanPath.split('\t')[0].trim()
  } else {
    const match = cleanPath.match(/^(.+?)\s{2,}\d{4}-\d{2}-\d{2}/)
    if (match) {
      cleanPath = match[1].trim()
    }
  }

  // 移除 a/ 或 b/ 前缀
  if (cleanPath.startsWith('a/') || cleanPath.startsWith('b/')) {
    cleanPath = cleanPath.slice(2)
  }

  return cleanPath
}

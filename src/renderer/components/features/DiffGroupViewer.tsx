/**
 * 按文件分组的 Diff 预览组件
 * 每个文件独立展示，支持单独应用
 */

import React, { useState, useMemo } from 'react'
import { CyberButton } from '../ui'

interface DiffGroupViewerProps {
  diffContent: string
  onApply?: (diffContent: string) => void
  onApplyAll?: () => void
  className?: string
}

/**
 * 从合并的 diff 文本中解析出每个文件的独立 diff
 */
function splitDiffByFile(diffContent: string): Array<{ filePath: string; diff: string; stats: { additions: number; deletions: number } }> {
  const files: Array<{ filePath: string; diff: string; stats: { additions: number; deletions: number } }> = []

  // 按 "--- " 分割文件
  const lines = diffContent.split('\n')
  let currentFile: { path: string; lines: string[] } | null = null

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]

    if (line.startsWith('--- ')) {
      // 保存前一个文件
      if (currentFile) {
        const diff = currentFile.lines.join('\n')
        const additions = currentFile.lines.filter(l => l.startsWith('+') && !l.startsWith('+++')).length
        const deletions = currentFile.lines.filter(l => l.startsWith('-') && !l.startsWith('---')).length
        files.push({
          filePath: currentFile.path,
          diff,
          stats: { additions, deletions }
        })
      }

      // 解析新文件路径
      let filePath = line.slice(4).trim()
      if (filePath.startsWith('a/')) filePath = filePath.slice(2)
      if (filePath.includes('\t')) filePath = filePath.split('\t')[0].trim()

      // 检查下一行 +++
      if (i + 1 < lines.length && lines[i + 1].startsWith('+++ ')) {
        let newPath = lines[i + 1].slice(4).trim()
        if (newPath.startsWith('b/')) newPath = newPath.slice(2)
        if (newPath.includes('\t')) newPath = newPath.split('\t')[0].trim()
        if (newPath !== '/dev/null') filePath = newPath
      }

      currentFile = { path: filePath, lines: [line] }
    } else if (currentFile) {
      currentFile.lines.push(line)
    }
  }

  // 保存最后一个文件
  if (currentFile) {
    const diff = currentFile.lines.join('\n')
    const additions = currentFile.lines.filter(l => l.startsWith('+') && !l.startsWith('+++')).length
    const deletions = currentFile.lines.filter(l => l.startsWith('-') && !l.startsWith('---')).length
    files.push({
      filePath: currentFile.path,
      diff,
      stats: { additions, deletions }
    })
  }

  return files
}

export const DiffGroupViewer: React.FC<DiffGroupViewerProps> = ({
  diffContent,
  onApply,
  onApplyAll,
  className = ''
}) => {
  const [expandedFiles, setExpandedFiles] = useState<Set<string>>(new Set())

  const files = useMemo(() => splitDiffByFile(diffContent), [diffContent])

  const toggleFile = (filePath: string) => {
    const newExpanded = new Set(expandedFiles)
    if (newExpanded.has(filePath)) {
      newExpanded.delete(filePath)
    } else {
      newExpanded.add(filePath)
    }
    setExpandedFiles(newExpanded)
  }

  const expandAll = () => {
    setExpandedFiles(new Set(files.map(f => f.filePath)))
  }

  const collapseAll = () => {
    setExpandedFiles(new Set())
  }

  if (files.length === 0) {
    return (
      <div className={`text-cyber-gray text-center text-sm py-8 ${className}`}>
        没有检测到 diff 内容
      </div>
    )
  }

  const totalAdditions = files.reduce((sum, f) => sum + f.stats.additions, 0)
  const totalDeletions = files.reduce((sum, f) => sum + f.stats.deletions, 0)

  return (
    <div className={`flex flex-col gap-3 ${className}`}>
      {/* 汇总栏 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-sm text-ghost-white">
            {files.length} 个文件
          </span>
          <span className="text-sm text-success-green">+{totalAdditions}</span>
          <span className="text-sm text-error-red">-{totalDeletions}</span>
        </div>
        <div className="flex gap-2">
          <CyberButton variant="ghost" onClick={expandAll}>
            全部展开
          </CyberButton>
          <CyberButton variant="ghost" onClick={collapseAll}>
            全部折叠
          </CyberButton>
          {onApplyAll && (
            <CyberButton variant="success" onClick={onApplyAll}>
              应用全部修改
            </CyberButton>
          )}
        </div>
      </div>

      {/* 文件列表 */}
      {files.map((file, idx) => {
        const isExpanded = expandedFiles.has(file.filePath)

        return (
          <div
            key={idx}
            className="border border-shadow-gray rounded-md overflow-hidden"
          >
            {/* 文件头 */}
            <div
              className="flex items-center justify-between px-3 py-2 bg-shadow-gray/20 cursor-pointer hover:bg-shadow-gray/30 transition-colors"
              onClick={() => toggleFile(file.filePath)}
            >
              <div className="flex items-center gap-3">
                <span className="text-xs text-cyber-gray">
                  {isExpanded ? '▼' : '▶'}
                </span>
                <span className="text-sm text-ghost-white font-mono">
                  {file.filePath}
                </span>
                <span className="text-xs text-success-green">+{file.stats.additions}</span>
                <span className="text-xs text-error-red">-{file.stats.deletions}</span>
              </div>
              {onApply && (
                <CyberButton
                  variant="secondary"
                  onClick={(e) => {
                    e.stopPropagation()
                    onApply(file.diff)
                  }}
                >
                  应用此文件
                </CyberButton>
              )}
            </div>

            {/* Diff 内容 */}
            {isExpanded && (
              <pre className="bg-deep-space/60 p-3 text-sm font-mono overflow-x-auto max-h-96 overflow-y-auto">
                {file.diff.split('\n').map((line, i) => {
                  let className = 'text-ghost-white'
                  if (line.startsWith('+') && !line.startsWith('+++')) {
                    className = 'text-success-green bg-success-green/5'
                  } else if (line.startsWith('-') && !line.startsWith('---')) {
                    className = 'text-error-red bg-error-red/5'
                  } else if (line.startsWith('@@')) {
                    className = 'text-neon-cyan'
                  } else if (line.startsWith('---') || line.startsWith('+++')) {
                    className = 'text-warning-yellow'
                  }
                  return (
                    <div key={i} className={className}>
                      {line}
                    </div>
                  )
                })}
              </pre>
            )}
          </div>
        )
      })}
    </div>
  )
}

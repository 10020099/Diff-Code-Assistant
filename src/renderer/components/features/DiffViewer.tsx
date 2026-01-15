import React, { useMemo } from 'react'
import { cn } from '../../utils/cn'

interface DiffViewerProps {
  content: string
  className?: string
}

export const DiffViewer: React.FC<DiffViewerProps> = ({ content, className }) => {
  const lines = useMemo(() => {
    if (!content) return []
    return content.split('\n').map((line, index) => ({
      number: index + 1,
      content: line,
      type: getLineType(line)
    }))
  }, [content])

  if (!content) {
    return (
      <div className={cn('flex items-center justify-center h-full text-cyber-gray', className)}>
        请输入 Diff 内容
      </div>
    )
  }

  return (
    <div className={cn('font-mono text-sm overflow-auto bg-deep-space rounded-lg', className)}>
      {lines.map((line) => (
        <div
          key={line.number}
          className={cn(
            'flex',
            line.type === 'add' && 'bg-success-green/10',
            line.type === 'delete' && 'bg-error-red/10',
            line.type === 'hunk' && 'bg-neon-purple/10'
          )}
        >
          <span className="w-12 flex-shrink-0 text-right pr-3 py-0.5 text-cyber-gray select-none border-r border-shadow-gray">
            {line.number}
          </span>
          <pre
            className={cn(
              'flex-1 px-3 py-0.5 whitespace-pre overflow-x-auto',
              line.type === 'add' && 'text-success-green',
              line.type === 'delete' && 'text-error-red',
              line.type === 'header' && 'text-neon-cyan font-bold',
              line.type === 'hunk' && 'text-neon-purple',
              line.type === 'context' && 'text-cyber-gray'
            )}
          >
            {line.content}
          </pre>
        </div>
      ))}
    </div>
  )
}

function getLineType(line: string): 'add' | 'delete' | 'header' | 'hunk' | 'context' {
  if (line.startsWith('+++') || line.startsWith('---')) {
    return 'header'
  }
  if (line.startsWith('@@')) {
    return 'hunk'
  }
  if (line.startsWith('+')) {
    return 'add'
  }
  if (line.startsWith('-')) {
    return 'delete'
  }
  return 'context'
}

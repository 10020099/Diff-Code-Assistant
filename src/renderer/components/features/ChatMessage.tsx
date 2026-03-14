/**
 * 对话消息组件 - 单条消息（用户/AI）
 * 支持 Diff 块高亮显示
 */

import React from 'react'

interface ChatMessageProps {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp?: number
  isStreaming?: boolean
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  role,
  content,
  timestamp,
  isStreaming
}) => {
  const isUser = role === 'user'

  // 渲染内容，高亮 ```diff 代码块
  const renderContent = (text: string) => {
    const parts: React.ReactNode[] = []
    const regex = /```(\w*)\s*\n([\s\S]*?)```/g
    let lastIndex = 0
    let match

    while ((match = regex.exec(text)) !== null) {
      // 普通文本
      if (match.index > lastIndex) {
        parts.push(
          <span key={lastIndex} className="whitespace-pre-wrap">
            {text.slice(lastIndex, match.index)}
          </span>
        )
      }

      const lang = match[1]
      const code = match[2]

      if (lang === 'diff') {
        // Diff 代码块特殊渲染
        parts.push(
          <div key={match.index} className="my-2 rounded-md overflow-hidden border border-neon-cyan/30">
            <div className="bg-neon-cyan/10 px-3 py-1 text-xs text-neon-cyan font-mono">
              DIFF
            </div>
            <pre className="bg-deep-space/80 p-3 text-sm font-mono overflow-x-auto">
              {code.split('\n').map((line, i) => {
                let className = 'text-ghost-white'
                if (line.startsWith('+') && !line.startsWith('+++')) {
                  className = 'text-success-green bg-success-green/10'
                } else if (line.startsWith('-') && !line.startsWith('---')) {
                  className = 'text-error-red bg-error-red/10'
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
          </div>
        )
      } else {
        // 其他代码块
        parts.push(
          <pre key={match.index} className="my-2 bg-deep-space/80 rounded-md p-3 text-sm font-mono overflow-x-auto border border-shadow-gray">
            <code>{code}</code>
          </pre>
        )
      }

      lastIndex = match.index + match[0].length
    }

    // 剩余文本
    if (lastIndex < text.length) {
      parts.push(
        <span key={lastIndex} className="whitespace-pre-wrap">
          {text.slice(lastIndex)}
        </span>
      )
    }

    return parts
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[85%] rounded-lg px-4 py-3 ${
          isUser
            ? 'bg-neon-cyan/20 border border-neon-cyan/40 text-ghost-white'
            : 'bg-shadow-gray/30 border border-shadow-gray text-ghost-white'
        }`}
      >
        {/* 角色标签 */}
        <div className="flex items-center gap-2 mb-1">
          <span
            className={`text-xs font-bold ${
              isUser ? 'text-neon-cyan' : 'text-neon-magenta'
            }`}
          >
            {isUser ? 'YOU' : 'AI'}
          </span>
          {timestamp && (
            <span className="text-xs text-cyber-gray">
              {new Date(timestamp).toLocaleTimeString()}
            </span>
          )}
          {isStreaming && (
            <span className="text-xs text-neon-cyan animate-pulse">● 生成中...</span>
          )}
        </div>

        {/* 消息内容 */}
        <div className="text-sm leading-relaxed">{renderContent(content)}</div>
      </div>
    </div>
  )
}

/**
 * 聊天输入框组件
 * 支持 Shift+Enter 换行，Enter 发送
 */

import React, { useState, useRef, useEffect } from 'react'
import { CyberButton } from '../ui'

interface ChatInputProps {
  onSend: (message: string) => void
  disabled?: boolean
  placeholder?: string
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSend,
  disabled = false,
  placeholder = '输入修改指令...'
}) => {
  const [input, setInput] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSend = () => {
    const trimmed = input.trim()
    if (!trimmed || disabled) return

    onSend(trimmed)
    setInput('')

    // 重置高度
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // 自动调整高度
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`
    }
  }, [input])

  return (
    <div className="flex gap-2 items-end">
      <textarea
        ref={textareaRef}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        rows={1}
        className={`
          flex-1 resize-none rounded-md px-3 py-2
          bg-deep-space/80 border border-shadow-gray
          text-ghost-white text-sm font-mono
          placeholder:text-cyber-gray/50
          focus:outline-none focus:border-neon-cyan/60
          transition-colors duration-200
          disabled:opacity-50 disabled:cursor-not-allowed
        `}
      />
      <CyberButton
        onClick={handleSend}
        disabled={disabled || !input.trim()}
        variant="primary"
      >
        {disabled ? '生成中...' : '发送'}
      </CyberButton>
    </div>
  )
}

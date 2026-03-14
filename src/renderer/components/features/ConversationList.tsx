/**
 * 对话历史侧边栏
 */

import React from 'react'
import { useChatStore, ConversationSummary } from '../../stores/chatStore'
import { CyberButton } from '../ui'

interface ConversationListProps {
  className?: string
}

export const ConversationList: React.FC<ConversationListProps> = ({
  className = ''
}) => {
  const {
    conversationList,
    currentConversation,
    loadConversation,
    deleteConversation,
    createNewConversation
  } = useChatStore()

  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp)
    const now = new Date()
    const isToday = date.toDateString() === now.toDateString()

    if (isToday) {
      return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    }
    return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
  }

  return (
    <div className={`flex flex-col h-full ${className}`}>
      <div className="flex items-center justify-between px-3 py-2 border-b border-shadow-gray">
        <span className="text-sm text-neon-cyan font-bold">对话历史</span>
        <CyberButton
          variant="ghost"
          onClick={() => createNewConversation(null)}
        >
          + 新对话
        </CyberButton>
      </div>

      <div className="flex-1 overflow-y-auto">
        {conversationList.length === 0 ? (
          <div className="text-center text-cyber-gray text-sm py-8">
            暂无历史对话
          </div>
        ) : (
          conversationList.map((conv) => (
            <div
              key={conv.id}
              className={`
                px-3 py-2 border-b border-shadow-gray/30 cursor-pointer
                hover:bg-shadow-gray/20 transition-colors
                ${currentConversation?.id === conv.id ? 'bg-neon-cyan/10 border-l-2 border-l-neon-cyan' : ''}
              `}
              onClick={() => loadConversation(conv.id)}
            >
              <div className="flex items-center justify-between">
                <span className="text-sm text-ghost-white truncate flex-1">
                  {conv.title}
                </span>
                <button
                  className="text-cyber-gray hover:text-error-red text-xs ml-2 transition-colors"
                  onClick={(e) => {
                    e.stopPropagation()
                    if (confirm('确定删除此对话？')) {
                      deleteConversation(conv.id)
                    }
                  }}
                >
                  ✕
                </button>
              </div>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-xs text-cyber-gray">
                  {conv.messageCount} 条消息
                </span>
                <span className="text-xs text-cyber-gray">
                  {formatTime(conv.updatedAt)}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

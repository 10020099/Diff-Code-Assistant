/**
 * AI 修改页面 - 核心页面
 * 集成对话、Diff 预览、应用修改
 */

import React, { useEffect, useRef, useMemo } from 'react'
import { useProjectStore } from '../stores/projectStore'
import { useSettingsStore } from '../stores/settingsStore'
import { useChatStore, extractDiffBlocks } from '../stores/chatStore'
import { useDiffStore } from '../stores/diffStore'
import { CyberButton, CyberCard } from '../components/ui'
import { ChatMessage, ChatInput, DiffGroupViewer, ConversationList } from '../components/features'

export const AIModify: React.FC = () => {
  const { projectRoot, scanResult, selectedFiles, context } = useProjectStore()
  const { config, getActiveProvider } = useSettingsStore()
  const {
    currentConversation,
    streamingContent,
    isStreaming,
    showHistory,
    setShowHistory,
    createNewConversation,
    addMessage,
    appendStreamingContent,
    setStreamingContent,
    setIsStreaming,
    finalizeStreaming,
    saveCurrentConversation,
    loadConversationList
  } = useChatStore()
  const { setDiffContent } = useDiffStore()

  const messagesEndRef = useRef<HTMLDivElement>(null)

  // 初始化
  useEffect(() => {
    loadConversationList()
    if (!currentConversation) {
      createNewConversation(projectRoot)
    }
  }, [])

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [currentConversation?.messages, streamingContent])

  // 注册流式事件监听
  useEffect(() => {
    const api = (window as any).api

    const unsubToken = api.llm.onStreamToken((data: { content: string }) => {
      appendStreamingContent(data.content)
    })

    const unsubDone = api.llm.onStreamDone((_data: { content: string; usage?: unknown; aborted?: boolean }) => {
      finalizeStreaming()
      // 保存对话
      setTimeout(() => {
        saveCurrentConversation()
      }, 100)
    })

    const unsubError = api.llm.onStreamError((data: { error: string }) => {
      setIsStreaming(false)
      setStreamingContent('')
      alert(`AI 响应错误: ${data.error}`)
    })

    return () => {
      unsubToken()
      unsubDone()
      unsubError()
    }
  }, [])

  // 发送消息
  const handleSend = async (messageContent: string) => {
    const provider = getActiveProvider()
    if (!provider) {
      alert('请先在设置页面配置 API 提供商')
      return
    }

    if (!currentConversation) {
      createNewConversation(projectRoot)
    }

    // 构建第一次的上下文消息
    const isFirstMessage = (currentConversation?.messages.length || 0) === 0
    let userContent = messageContent

    if (isFirstMessage && context) {
      userContent = `以下是项目的上下文信息：

${context}

=== 用户指令 ===
${messageContent}`
    }

    // 添加用户消息
    const userMessage = {
      id: Date.now().toString(36) + Math.random().toString(36).slice(2, 8),
      role: 'user' as const,
      content: userContent,
      timestamp: Date.now()
    }
    addMessage(userMessage)

    // 构建历史消息
    const history = [
      ...(currentConversation?.messages || []).map(m => ({
        role: m.role,
        content: m.content
      })),
      { role: 'user' as const, content: userContent }
    ]

    // 开始流式请求
    setIsStreaming(true)
    setStreamingContent('')

    try {
      await (window as any).api.llm.chatStream(
        provider,
        history,
        config.systemPrompt
      )
    } catch (error) {
      setIsStreaming(false)
      alert(`请求失败: ${error}`)
    }
  }

  // 停止生成
  const handleStop = async () => {
    try {
      await (window as any).api.llm.stopStream()
    } catch (error) {
      console.error('停止失败:', error)
    }
  }

  // 从当前对话中收集所有 diff 块
  const allDiffBlocks = useMemo(() => {
    if (!currentConversation) return []
    const blocks: string[] = []
    for (const msg of currentConversation.messages) {
      if (msg.role === 'assistant' && msg.diffBlocks) {
        blocks.push(...msg.diffBlocks)
      }
    }
    // 也包含正在流式生成中的 diff
    if (streamingContent) {
      blocks.push(...extractDiffBlocks(streamingContent))
    }
    return blocks
  }, [currentConversation?.messages, streamingContent])

  // 合并所有 diff 为一个字符串
  const combinedDiff = useMemo(() => allDiffBlocks.join('\n'), [allDiffBlocks])

  // 应用 diff
  const handleApplyDiff = async (diffToApply: string) => {
    if (!projectRoot) {
      alert('请先在项目设置页面选择项目目录')
      return
    }

    const validation = await (window as any).api.diff.validate(diffToApply)
    if (!validation.isValid) {
      alert(`Diff 格式验证失败:\n${validation.message}`)
      return
    }

    if (!confirm('确定要应用此修改？（将自动创建备份）')) return

    try {
      const result = await (window as any).api.diff.apply(diffToApply, projectRoot, {
        createBackup: true,
        dryRun: false
      })

      let msg = `应用完成!\n成功: ${result.successCount} 个文件\n失败: ${result.errorCount} 个文件`
      if (result.backupDir) {
        msg += `\n\n备份位置: ${result.backupDir}`
      }
      if (result.errors?.length > 0) {
        msg += `\n\n错误:\n${result.errors.join('\n')}`
      }
      alert(msg)
    } catch (error) {
      alert(`应用失败: ${error}`)
    }
  }

  const handleApplyAll = () => {
    if (combinedDiff) {
      handleApplyDiff(combinedDiff)
    }
  }

  const activeProvider = getActiveProvider()

  return (
    <div className="h-full flex">
      {/* 左侧：对话历史侧边栏 */}
      {showHistory && (
        <div className="w-64 flex-shrink-0 border-r border-shadow-gray bg-deep-space/50">
          <ConversationList />
        </div>
      )}

      {/* 中间：对话区域 */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* 顶部工具栏 */}
        <div className="flex-shrink-0 flex items-center justify-between px-4 py-2 border-b border-shadow-gray">
          <div className="flex items-center gap-3">
            <CyberButton
              variant="ghost"
              onClick={() => setShowHistory(!showHistory)}
            >
              {showHistory ? '◀ 隐藏' : '▶ 历史'}
            </CyberButton>
            <CyberButton
              variant="ghost"
              onClick={() => createNewConversation(projectRoot)}
            >
              + 新对话
            </CyberButton>
          </div>

          <div className="flex items-center gap-3">
            {activeProvider ? (
              <span className="text-xs text-neon-cyan">
                {activeProvider.name} / {activeProvider.model}
              </span>
            ) : (
              <span className="text-xs text-error-red">
                未配置 API
              </span>
            )}
            {projectRoot ? (
              <span className="text-xs text-cyber-gray truncate max-w-48">
                📁 {projectRoot}
              </span>
            ) : (
              <span className="text-xs text-warning-yellow">
                未选择项目
              </span>
            )}
          </div>
        </div>

        {/* 消息列表 */}
        <div className="flex-1 overflow-y-auto px-4 py-4">
          {(!currentConversation || currentConversation.messages.length === 0) && !isStreaming && (
            <div className="text-center text-cyber-gray py-16">
              <div className="text-4xl mb-4">🤖</div>
              <p className="text-lg mb-2">准备开始 AI 辅助代码修改</p>
              <p className="text-sm">
                {context ? '项目上下文已就绪，输入修改指令开始对话' : '请先在「项目设置」页面扫描项目并生成上下文'}
              </p>
            </div>
          )}

          {currentConversation?.messages.map((msg) => (
            <ChatMessage
              key={msg.id}
              role={msg.role}
              content={msg.content}
              timestamp={msg.timestamp}
            />
          ))}

          {/* 流式响应中的消息 */}
          {isStreaming && streamingContent && (
            <ChatMessage
              role="assistant"
              content={streamingContent}
              isStreaming={true}
            />
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* 输入区域 */}
        <div className="flex-shrink-0 px-4 py-3 border-t border-shadow-gray">
          {isStreaming ? (
            <div className="flex justify-center">
              <CyberButton variant="secondary" onClick={handleStop}>
                ■ 停止生成
              </CyberButton>
            </div>
          ) : (
            <ChatInput
              onSend={handleSend}
              disabled={isStreaming || !activeProvider}
              placeholder={
                !activeProvider
                  ? '请先在设置中配置 API...'
                  : context
                    ? '输入代码修改指令...'
                    : '请先在项目设置中生成上下文...'
              }
            />
          )}
        </div>
      </div>

      {/* 右侧：Diff 预览面板 */}
      {allDiffBlocks.length > 0 && (
        <div className="w-96 flex-shrink-0 border-l border-shadow-gray flex flex-col">
          <div className="px-3 py-2 border-b border-shadow-gray">
            <span className="text-sm text-neon-cyan font-bold">Diff 预览</span>
          </div>
          <div className="flex-1 overflow-y-auto p-3">
            <DiffGroupViewer
              diffContent={combinedDiff}
              onApply={handleApplyDiff}
              onApplyAll={handleApplyAll}
            />
          </div>
        </div>
      )}
    </div>
  )
}

/**
 * LLM 提供商基类
 * 定义所有提供商必须实现的接口
 */

import { ProviderConfig, ChatMessage, ChatResponse, StreamEvent } from './types'

export abstract class LLMProviderBase {
  protected config: ProviderConfig

  constructor(config: ProviderConfig) {
    this.config = config
  }

  /**
   * 发送聊天请求（非流式）
   */
  abstract chat(messages: ChatMessage[], systemPrompt?: string): Promise<ChatResponse>

  /**
   * 发送聊天请求（流式）
   * 返回一个 AsyncGenerator，逐步 yield StreamEvent
   */
  abstract chatStream(
    messages: ChatMessage[],
    systemPrompt?: string
  ): AsyncGenerator<StreamEvent, void, unknown>

  /**
   * 测试连接是否正常
   */
  async testConnection(): Promise<{ success: boolean; message: string }> {
    try {
      const response = await this.chat(
        [{ role: 'user', content: 'Hi, reply with "ok" only.' }],
        'Reply with exactly "ok".'
      )
      if (response.success) {
        return { success: true, message: '连接成功' }
      }
      return { success: false, message: response.error || '未知错误' }
    } catch (error) {
      return { success: false, message: String(error) }
    }
  }

  /**
   * 获取配置
   */
  getConfig(): ProviderConfig {
    return this.config
  }

  /**
   * 构建请求头  (子类可覆盖)
   */
  protected buildHeaders(): Record<string, string> {
    return {
      'Content-Type': 'application/json'
    }
  }
}

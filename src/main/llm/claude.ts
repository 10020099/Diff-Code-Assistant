/**
 * Anthropic Claude Messages API 提供商
 */

import { LLMProviderBase } from './providerBase'
import { ChatMessage, ChatResponse, StreamEvent } from './types'

export class ClaudeProvider extends LLMProviderBase {
  protected buildHeaders(): Record<string, string> {
    return {
      'Content-Type': 'application/json',
      'x-api-key': this.config.apiKey,
      'anthropic-version': '2023-06-01'
    }
  }

  private buildBody(messages: ChatMessage[], systemPrompt?: string, stream = false) {
    // Claude 的 messages 不包含 system，system 单独传
    const msgs: Array<{ role: string; content: string }> = []

    for (const msg of messages) {
      if (msg.role !== 'system') {
        msgs.push({ role: msg.role, content: msg.content })
      }
    }

    // 确保消息列表不为空，且第一条是 user
    if (msgs.length === 0) {
      msgs.push({ role: 'user', content: '你好' })
    }

    const body: any = {
      model: this.config.model,
      messages: msgs,
      max_tokens: this.config.maxTokens || 16384,
      stream
    }

    // Claude 的 system 参数
    const systemContent = systemPrompt || messages.find(m => m.role === 'system')?.content
    if (systemContent) {
      body.system = systemContent
    }

    if (this.config.temperature !== undefined) {
      body.temperature = this.config.temperature
    }

    return body
  }

  async chat(messages: ChatMessage[], systemPrompt?: string): Promise<ChatResponse> {
    try {
      const url = `${this.config.baseUrl.replace(/\/+$/, '')}/v1/messages`
      const body = this.buildBody(messages, systemPrompt, false)

      const response = await fetch(url, {
        method: 'POST',
        headers: this.buildHeaders(),
        body: JSON.stringify(body)
      })

      if (!response.ok) {
        const errorText = await response.text()
        return { success: false, error: `HTTP ${response.status}: ${errorText}` }
      }

      const data = await response.json()

      let content = ''
      if (data.content) {
        for (const block of data.content) {
          if (block.type === 'text') {
            content += block.text
          }
        }
      }

      const usage = data.usage
        ? {
            promptTokens: data.usage.input_tokens || 0,
            completionTokens: data.usage.output_tokens || 0,
            totalTokens: (data.usage.input_tokens || 0) + (data.usage.output_tokens || 0)
          }
        : undefined

      return { success: true, content, usage }
    } catch (error) {
      return { success: false, error: String(error) }
    }
  }

  async *chatStream(
    messages: ChatMessage[],
    systemPrompt?: string
  ): AsyncGenerator<StreamEvent, void, unknown> {
    try {
      const url = `${this.config.baseUrl.replace(/\/+$/, '')}/v1/messages`
      const body = this.buildBody(messages, systemPrompt, true)

      const response = await fetch(url, {
        method: 'POST',
        headers: this.buildHeaders(),
        body: JSON.stringify(body)
      })

      if (!response.ok) {
        const errorText = await response.text()
        yield { type: 'error', error: `HTTP ${response.status}: ${errorText}` }
        return
      }

      const reader = response.body?.getReader()
      if (!reader) {
        yield { type: 'error', error: '无法获取响应流' }
        return
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          const trimmed = line.trim()

          if (trimmed.startsWith('event: ')) {
            continue
          }

          if (!trimmed.startsWith('data: ')) continue

          const data = trimmed.slice(6)

          try {
            const parsed = JSON.parse(data)

            switch (parsed.type) {
              case 'content_block_delta':
                if (parsed.delta?.type === 'text_delta' && parsed.delta?.text) {
                  yield { type: 'token', content: parsed.delta.text }
                }
                break

              case 'message_delta':
                if (parsed.usage) {
                  // Claude 在 message_delta 中返回 output_tokens
                }
                break

              case 'message_stop': {
                yield { type: 'done' }
                return
              }

              case 'error':
                yield {
                  type: 'error',
                  error: parsed.error?.message || '未知错误'
                }
                return
            }
          } catch {
            // 忽略解析错误
          }
        }
      }

      yield { type: 'done' }
    } catch (error) {
      yield { type: 'error', error: String(error) }
    }
  }
}

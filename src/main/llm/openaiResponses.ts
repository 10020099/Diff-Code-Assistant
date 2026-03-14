/**
 * OpenAI Responses API 提供商
 * 支持新的 Responses API 格式
 */

import { LLMProviderBase } from './providerBase'
import { ChatMessage, ChatResponse, StreamEvent } from './types'

export class OpenAIResponsesProvider extends LLMProviderBase {
  protected buildHeaders(): Record<string, string> {
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.config.apiKey}`
    }
  }

  private buildBody(messages: ChatMessage[], systemPrompt?: string, stream = false) {
    // Responses API 使用 input 数组
    const input: Array<{ role: string; content: string }> = []

    if (systemPrompt) {
      input.push({ role: 'developer', content: systemPrompt })
    }

    for (const msg of messages) {
      // Responses API 中 system → developer，其他角色保持不变
      const role = msg.role === 'system' ? 'developer' : msg.role
      input.push({ role, content: msg.content })
    }

    const body: any = {
      model: this.config.model,
      input,
      stream
    }

    if (this.config.maxTokens) {
      body.max_output_tokens = this.config.maxTokens
    }

    if (this.config.temperature !== undefined) {
      body.temperature = this.config.temperature
    }

    return body
  }

  async chat(messages: ChatMessage[], systemPrompt?: string): Promise<ChatResponse> {
    try {
      const url = `${this.config.baseUrl.replace(/\/+$/, '')}/responses`
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

      // Responses API 的返回格式
      // output 是一个数组，包含 message 类型的对象
      let content = ''
      if (data.output) {
        for (const item of data.output) {
          if (item.type === 'message' && item.content) {
            for (const part of item.content) {
              if (part.type === 'output_text') {
                content += part.text
              }
            }
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
      const url = `${this.config.baseUrl.replace(/\/+$/, '')}/responses`
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
          if (!trimmed) continue

          // Responses API 的 SSE 事件格式
          if (trimmed.startsWith('event: ')) {
            continue // 事件类型行，跳过
          }

          if (!trimmed.startsWith('data: ')) continue

          const data = trimmed.slice(6)

          try {
            const parsed = JSON.parse(data)

            // 处理不同的事件类型
            switch (parsed.type) {
              case 'response.output_text.delta':
                if (parsed.delta) {
                  yield { type: 'token', content: parsed.delta }
                }
                break

              case 'response.completed': {
                const usage = parsed.response?.usage
                  ? {
                      promptTokens: parsed.response.usage.input_tokens || 0,
                      completionTokens: parsed.response.usage.output_tokens || 0,
                      totalTokens:
                        (parsed.response.usage.input_tokens || 0) +
                        (parsed.response.usage.output_tokens || 0)
                    }
                  : undefined
                yield { type: 'done', usage }
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

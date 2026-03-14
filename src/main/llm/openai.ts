/**
 * OpenAI Chat Completions API 提供商
 * 兼容所有 OpenAI 格式的 API (包括中转)
 */

import { LLMProviderBase } from './providerBase'
import { ChatMessage, ChatResponse, StreamEvent } from './types'

export class OpenAIProvider extends LLMProviderBase {
  protected buildHeaders(): Record<string, string> {
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.config.apiKey}`
    }
  }

  private buildBody(messages: ChatMessage[], systemPrompt?: string, stream = false) {
    const msgs: Array<{ role: string; content: string }> = []

    if (systemPrompt) {
      msgs.push({ role: 'system', content: systemPrompt })
    }

    for (const msg of messages) {
      msgs.push({ role: msg.role, content: msg.content })
    }

    return {
      model: this.config.model,
      messages: msgs,
      max_tokens: this.config.maxTokens || 16384,
      temperature: this.config.temperature ?? 0.7,
      stream
    }
  }

  async chat(messages: ChatMessage[], systemPrompt?: string): Promise<ChatResponse> {
    try {
      const url = `${this.config.baseUrl.replace(/\/+$/, '')}/chat/completions`
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
      const content = data.choices?.[0]?.message?.content || ''
      const usage = data.usage
        ? {
            promptTokens: data.usage.prompt_tokens || 0,
            completionTokens: data.usage.completion_tokens || 0,
            totalTokens: data.usage.total_tokens || 0
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
      const url = `${this.config.baseUrl.replace(/\/+$/, '')}/chat/completions`
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
          if (!trimmed || !trimmed.startsWith('data: ')) continue

          const data = trimmed.slice(6)
          if (data === '[DONE]') {
            yield { type: 'done' }
            return
          }

          try {
            const parsed = JSON.parse(data)
            const delta = parsed.choices?.[0]?.delta?.content
            if (delta) {
              yield { type: 'token', content: delta }
            }

            // 检查是否结束
            if (parsed.choices?.[0]?.finish_reason) {
              const usage = parsed.usage
                ? {
                    promptTokens: parsed.usage.prompt_tokens || 0,
                    completionTokens: parsed.usage.completion_tokens || 0,
                    totalTokens: parsed.usage.total_tokens || 0
                  }
                : undefined
              yield { type: 'done', usage }
              return
            }
          } catch {
            // 忽略解析错误的行
          }
        }
      }

      yield { type: 'done' }
    } catch (error) {
      yield { type: 'error', error: String(error) }
    }
  }
}

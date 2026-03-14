/**
 * Google Gemini API 提供商
 */

import { LLMProviderBase } from './providerBase'
import { ChatMessage, ChatResponse, StreamEvent } from './types'

export class GeminiProvider extends LLMProviderBase {
  private getApiUrl(stream = false): string {
    const baseUrl = this.config.baseUrl.replace(/\/+$/, '')
    const action = stream ? 'streamGenerateContent' : 'generateContent'

    // Gemini API 格式: /v1beta/models/{model}:{action}?key={apiKey}
    return `${baseUrl}/v1beta/models/${this.config.model}:${action}?key=${this.config.apiKey}`
  }

  private buildBody(messages: ChatMessage[], systemPrompt?: string) {
    // Gemini 使用 contents 数组，角色只有 user 和 model
    const contents: Array<{ role: string; parts: Array<{ text: string }> }> = []

    for (const msg of messages) {
      if (msg.role === 'system') continue // system 单独处理

      contents.push({
        role: msg.role === 'assistant' ? 'model' : 'user',
        parts: [{ text: msg.content }]
      })
    }

    // 确保不为空
    if (contents.length === 0) {
      contents.push({
        role: 'user',
        parts: [{ text: '你好' }]
      })
    }

    const body: any = {
      contents,
      generationConfig: {
        maxOutputTokens: this.config.maxTokens || 16384,
        temperature: this.config.temperature ?? 0.7
      }
    }

    // Gemini 的 system instruction
    const systemContent = systemPrompt || messages.find(m => m.role === 'system')?.content
    if (systemContent) {
      body.systemInstruction = {
        parts: [{ text: systemContent }]
      }
    }

    return body
  }

  async chat(messages: ChatMessage[], systemPrompt?: string): Promise<ChatResponse> {
    try {
      const url = this.getApiUrl(false)
      const body = this.buildBody(messages, systemPrompt)

      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })

      if (!response.ok) {
        const errorText = await response.text()
        return { success: false, error: `HTTP ${response.status}: ${errorText}` }
      }

      const data = await response.json()

      let content = ''
      if (data.candidates?.[0]?.content?.parts) {
        for (const part of data.candidates[0].content.parts) {
          if (part.text) {
            content += part.text
          }
        }
      }

      const usage = data.usageMetadata
        ? {
            promptTokens: data.usageMetadata.promptTokenCount || 0,
            completionTokens: data.usageMetadata.candidatesTokenCount || 0,
            totalTokens: data.usageMetadata.totalTokenCount || 0
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
      // Gemini 流式使用 alt=sse 参数
      const url = this.getApiUrl(true) + '&alt=sse'
      const body = this.buildBody(messages, systemPrompt)

      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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
          if (!trimmed.startsWith('data: ')) continue

          const data = trimmed.slice(6)

          try {
            const parsed = JSON.parse(data)

            if (parsed.candidates?.[0]?.content?.parts) {
              for (const part of parsed.candidates[0].content.parts) {
                if (part.text) {
                  yield { type: 'token', content: part.text }
                }
              }
            }

            // 检查是否结束
            if (parsed.candidates?.[0]?.finishReason) {
              const usage = parsed.usageMetadata
                ? {
                    promptTokens: parsed.usageMetadata.promptTokenCount || 0,
                    completionTokens: parsed.usageMetadata.candidatesTokenCount || 0,
                    totalTokens: parsed.usageMetadata.totalTokenCount || 0
                  }
                : undefined
              yield { type: 'done', usage }
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

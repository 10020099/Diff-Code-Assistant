/**
 * LLM 模块统一入口
 * 工厂方法：根据提供商类型创建对应的实例
 */

import { ProviderConfig } from './types'
import { LLMProviderBase } from './providerBase'
import { OpenAIProvider } from './openai'
import { OpenAIResponsesProvider } from './openaiResponses'
import { ClaudeProvider } from './claude'
import { GeminiProvider } from './gemini'
import { DeepSeekProvider } from './deepseek'

export function createProvider(config: ProviderConfig): LLMProviderBase {
  switch (config.provider) {
    case 'openai':
      return new OpenAIProvider(config)
    case 'openai-responses':
      return new OpenAIResponsesProvider(config)
    case 'claude':
      return new ClaudeProvider(config)
    case 'gemini':
      return new GeminiProvider(config)
    case 'deepseek':
      return new DeepSeekProvider(config)
    default:
      throw new Error(`不支持的提供商类型: ${config.provider}`)
  }
}

export * from './types'
export { LLMProviderBase } from './providerBase'

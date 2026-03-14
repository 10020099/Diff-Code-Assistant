/**
 * DeepSeek API 提供商
 * 基于 OpenAI 兼容格式
 */

import { OpenAIProvider } from './openai'

export class DeepSeekProvider extends OpenAIProvider {
  // DeepSeek 完全兼容 OpenAI Chat Completions API
  // 只是默认 base URL 和模型不同
  // 直接继承 OpenAIProvider 即可
}

/**
 * 设置页面 - API 提供商配置管理
 */

import React, { useState, useEffect } from 'react'
import { useSettingsStore, ProviderConfig, LLMProvider } from '../stores/settingsStore'
import { CyberButton, CyberCard, CyberInput, CyberTextarea } from '../components/ui'

const PROVIDER_OPTIONS: Array<{ value: LLMProvider; label: string; defaultUrl: string; defaultModel: string }> = [
  { value: 'openai', label: 'OpenAI (Chat Completions)', defaultUrl: 'https://api.openai.com/v1', defaultModel: 'gpt-4o' },
  { value: 'openai-responses', label: 'OpenAI (Responses API)', defaultUrl: 'https://api.openai.com/v1', defaultModel: 'gpt-4o' },
  { value: 'claude', label: 'Anthropic Claude', defaultUrl: 'https://api.anthropic.com', defaultModel: 'claude-sonnet-4-20250514' },
  { value: 'gemini', label: 'Google Gemini', defaultUrl: 'https://generativelanguage.googleapis.com', defaultModel: 'gemini-2.5-flash' },
  { value: 'deepseek', label: 'DeepSeek', defaultUrl: 'https://api.deepseek.com', defaultModel: 'deepseek-chat' }
]

function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 8)
}

export const Settings: React.FC = () => {
  const {
    config,
    addProvider,
    updateProvider,
    removeProvider,
    setActiveProvider,
    setSystemPrompt,
    loadConfig,
    saveConfig
  } = useSettingsStore()

  const [editingId, setEditingId] = useState<string | null>(null)
  const [showAddForm, setShowAddForm] = useState(false)
  const [testingId, setTestingId] = useState<string | null>(null)
  const [testResult, setTestResult] = useState<{ id: string; success: boolean; message: string } | null>(null)

  // 新增提供商表单
  const [newProvider, setNewProvider] = useState<Partial<ProviderConfig>>({
    provider: 'openai',
    name: '',
    apiKey: '',
    baseUrl: 'https://api.openai.com/v1',
    model: 'gpt-4o',
    maxTokens: 16384,
    temperature: 0.7
  })

  // 初次加载配置
  useEffect(() => {
    loadConfig()
  }, [])

  // 选择提供商类型时更新默认值
  const handleProviderTypeChange = (type: LLMProvider) => {
    const option = PROVIDER_OPTIONS.find(o => o.value === type)
    if (option) {
      setNewProvider(prev => ({
        ...prev,
        provider: type,
        baseUrl: option.defaultUrl,
        model: option.defaultModel,
        name: prev?.name || option.label
      }))
    }
  }

  // 添加提供商
  const handleAdd = async () => {
    if (!newProvider.name || !newProvider.apiKey || !newProvider.baseUrl) {
      alert('请填写名称、API Key 和 Base URL')
      return
    }

    const providerConfig: ProviderConfig = {
      id: generateId(),
      name: newProvider.name || '',
      provider: newProvider.provider || 'openai',
      apiKey: newProvider.apiKey || '',
      baseUrl: newProvider.baseUrl || '',
      model: newProvider.model || '',
      maxTokens: newProvider.maxTokens || 16384,
      temperature: newProvider.temperature ?? 0.7
    }

    addProvider(providerConfig)
    setShowAddForm(false)
    setNewProvider({
      provider: 'openai',
      name: '',
      apiKey: '',
      baseUrl: 'https://api.openai.com/v1',
      model: 'gpt-4o',
      maxTokens: 16384,
      temperature: 0.7
    })

    // 自动保存
    setTimeout(saveConfig, 100)
  }

  // 测试连接
  const handleTest = async (provider: ProviderConfig) => {
    setTestingId(provider.id)
    setTestResult(null)

    try {
      const result = await (window as any).api.llm.testConnection(provider)
      setTestResult({ id: provider.id, success: result.success, message: result.message })
    } catch (error) {
      setTestResult({ id: provider.id, success: false, message: String(error) })
    } finally {
      setTestingId(null)
    }
  }

  // 删除
  const handleDelete = (id: string) => {
    if (confirm('确定删除此提供商配置？')) {
      removeProvider(id)
      setTimeout(saveConfig, 100)
    }
  }

  // 保存更新
  const handleUpdate = (id: string, updates: Partial<ProviderConfig>) => {
    updateProvider(id, updates)
    setTimeout(saveConfig, 100)
  }

  return (
    <div className="h-full flex flex-col overflow-y-auto">
      {/* 提供商列表 */}
      <CyberCard className="mb-4" title="API 提供商">
        <div className="space-y-3">
          {config.providers.length === 0 && !showAddForm && (
            <div className="text-center text-cyber-gray py-8">
              <p className="text-sm mb-3">尚未配置任何 API 提供商</p>
              <CyberButton onClick={() => setShowAddForm(true)}>
                添加提供商
              </CyberButton>
            </div>
          )}

          {config.providers.map((provider) => (
            <div
              key={provider.id}
              className={`
                border rounded-md p-3 transition-colors
                ${config.activeProviderId === provider.id
                  ? 'border-neon-cyan bg-neon-cyan/5'
                  : 'border-shadow-gray hover:border-shadow-gray/80'
                }
              `}
            >
              {editingId === provider.id ? (
                /* 编辑模式 */
                <div className="space-y-2">
                  <div className="flex gap-2">
                    <CyberInput
                      value={provider.name}
                      onChange={(e) => handleUpdate(provider.id, { name: e.target.value })}
                      placeholder="名称"
                      className="flex-1"
                    />
                    <select
                      value={provider.provider}
                      onChange={(e) => handleUpdate(provider.id, { provider: e.target.value as LLMProvider })}
                      className="bg-deep-space border border-shadow-gray text-ghost-white text-sm rounded px-2 py-1"
                    >
                      {PROVIDER_OPTIONS.map(opt => (
                        <option key={opt.value} value={opt.value}>{opt.label}</option>
                      ))}
                    </select>
                  </div>
                  <CyberInput
                    type="password"
                    value={provider.apiKey}
                    onChange={(e) => handleUpdate(provider.id, { apiKey: e.target.value })}
                    placeholder="API Key"
                  />
                  <CyberInput
                    value={provider.baseUrl}
                    onChange={(e) => handleUpdate(provider.id, { baseUrl: e.target.value })}
                    placeholder="Base URL"
                  />
                  <div className="flex gap-2 items-end">
                    <div className="flex-1">
                      <label className="text-xs text-cyber-gray mb-1 block">模型名称</label>
                      <CyberInput
                        value={provider.model}
                        onChange={(e) => handleUpdate(provider.id, { model: e.target.value })}
                        placeholder="模型名称"
                      />
                    </div>
                    <div className="w-32">
                      <label className="text-xs text-cyber-gray mb-1 block">最大输出</label>
                      <CyberInput
                        type="number"
                        value={provider.maxTokens || 16384}
                        onChange={(e) => handleUpdate(provider.id, { maxTokens: Number(e.target.value) })}
                        placeholder="16384"
                      />
                    </div>
                    <div className="w-24">
                      <label className="text-xs text-cyber-gray mb-1 block">温度</label>
                      <CyberInput
                        type="number"
                        value={provider.temperature ?? 0.7}
                        onChange={(e) => handleUpdate(provider.id, { temperature: Number(e.target.value) })}
                        placeholder="0.7"
                      />
                    </div>
                  </div>
                  <div className="flex justify-end">
                    <CyberButton variant="ghost" onClick={() => setEditingId(null)}>
                      完成
                    </CyberButton>
                  </div>
                </div>
              ) : (
                /* 展示模式 */
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <div
                      className={`w-2 h-2 rounded-full ${
                        config.activeProviderId === provider.id
                          ? 'bg-neon-cyan animate-pulse'
                          : 'bg-shadow-gray'
                      }`}
                    />
                    <div className="min-w-0">
                      <div className="text-sm text-ghost-white font-bold truncate">
                        {provider.name}
                      </div>
                      <div className="text-xs text-cyber-gray truncate">
                        {provider.model} · {provider.baseUrl}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 flex-shrink-0">
                    {testResult?.id === provider.id && (
                      <span className={`text-xs ${testResult.success ? 'text-success-green' : 'text-error-red'}`}>
                        {testResult.message}
                      </span>
                    )}
                    <CyberButton
                      variant="ghost"
                      onClick={() => handleTest(provider)}
                      loading={testingId === provider.id}
                    >
                      测试
                    </CyberButton>
                    {config.activeProviderId !== provider.id && (
                      <CyberButton
                        variant="secondary"
                        onClick={() => {
                          setActiveProvider(provider.id)
                          setTimeout(saveConfig, 100)
                        }}
                      >
                        启用
                      </CyberButton>
                    )}
                    <CyberButton variant="ghost" onClick={() => setEditingId(provider.id)}>
                      编辑
                    </CyberButton>
                    <CyberButton variant="ghost" onClick={() => handleDelete(provider.id)}>
                      删除
                    </CyberButton>
                  </div>
                </div>
              )}
            </div>
          ))}

          {/* 添加新提供商表单 */}
          {showAddForm && (
            <div className="border border-neon-cyan/30 rounded-md p-3 space-y-2">
              <div className="text-sm text-neon-cyan font-bold mb-2">添加新提供商</div>

              <div className="flex gap-2">
                <CyberInput
                  value={newProvider.name || ''}
                  onChange={(e) => setNewProvider(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="显示名称"
                  className="flex-1"
                />
                <select
                  value={newProvider.provider}
                  onChange={(e) => handleProviderTypeChange(e.target.value as LLMProvider)}
                  className="bg-deep-space border border-shadow-gray text-ghost-white text-sm rounded px-2 py-1"
                >
                  {PROVIDER_OPTIONS.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>

              <CyberInput
                type="password"
                value={newProvider.apiKey || ''}
                onChange={(e) => setNewProvider(prev => ({ ...prev, apiKey: e.target.value }))}
                placeholder="API Key"
              />

              <CyberInput
                value={newProvider.baseUrl || ''}
                onChange={(e) => setNewProvider(prev => ({ ...prev, baseUrl: e.target.value }))}
                placeholder="Base URL (支持自定义中转地址)"
              />

              <div className="flex gap-2 items-end">
                <div className="flex-1">
                  <label className="text-xs text-cyber-gray mb-1 block">模型名称</label>
                  <CyberInput
                    value={newProvider.model || ''}
                    onChange={(e) => setNewProvider(prev => ({ ...prev, model: e.target.value }))}
                    placeholder="模型名称"
                  />
                </div>
                <div className="w-32">
                  <label className="text-xs text-cyber-gray mb-1 block">最大输出</label>
                  <CyberInput
                    type="number"
                    value={newProvider.maxTokens || 16384}
                    onChange={(e) => setNewProvider(prev => ({ ...prev, maxTokens: Number(e.target.value) }))}
                    placeholder="16384"
                  />
                </div>
                <div className="w-24">
                  <label className="text-xs text-cyber-gray mb-1 block">温度</label>
                  <CyberInput
                    type="number"
                    value={newProvider.temperature ?? 0.7}
                    onChange={(e) => setNewProvider(prev => ({ ...prev, temperature: Number(e.target.value) }))}
                    placeholder="0.7"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2">
                <CyberButton variant="ghost" onClick={() => setShowAddForm(false)}>
                  取消
                </CyberButton>
                <CyberButton variant="primary" onClick={handleAdd}>
                  添加
                </CyberButton>
              </div>
            </div>
          )}

          {config.providers.length > 0 && !showAddForm && (
            <CyberButton
              variant="ghost"
              onClick={() => setShowAddForm(true)}
              className="w-full"
            >
              + 添加提供商
            </CyberButton>
          )}
        </div>
      </CyberCard>

      {/* 系统提示词 */}
      <CyberCard className="mb-4" title="系统提示词">
        <CyberTextarea
          value={config.systemPrompt}
          onChange={(e) => {
            setSystemPrompt(e.target.value)
            setTimeout(saveConfig, 500)
          }}
          placeholder="系统提示词..."
          className="h-48"
        />
        <div className="flex justify-end mt-2">
          <CyberButton
            variant="ghost"
            onClick={() => {
              if (confirm('确定重置为默认系统提示词？')) {
                setSystemPrompt('')
                loadConfig()
              }
            }}
          >
            重置为默认
          </CyberButton>
        </div>
      </CyberCard>
    </div>
  )
}

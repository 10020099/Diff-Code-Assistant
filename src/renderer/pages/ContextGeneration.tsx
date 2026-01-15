import React, { useState } from 'react'
import { useProjectStore } from '../stores/projectStore'
import { CyberButton, CyberInput, CyberTextarea, CyberCard } from '../components/ui'

interface ContextGenerationProps {
  onNext: () => void
}

export const ContextGeneration: React.FC<ContextGenerationProps> = ({ onNext }) => {
  const { context } = useProjectStore()
  const [prompt, setPrompt] = useState('')
  const [fullPrompt, setFullPrompt] = useState('')

  const handleGeneratePrompt = () => {
    if (!context) {
      alert('请先生成上下文')
      return
    }

    if (!prompt.trim()) {
      alert('请输入LLM指令')
      return
    }

    const generated = `请根据以下项目上下文和指令，生成代码修改的diff格式输出：

${context}

=== 用户指令 ===
${prompt}

=== 要求 ===
1. 仔细分析项目结构和代码内容
2. 根据指令生成相应的代码修改
3. 以标准diff格式输出所有更改
4. 确保修改的一致性和正确性

请生成diff格式的修改建议：`

    setFullPrompt(generated)
  }

  const handleCopyPrompt = async () => {
    if (!fullPrompt) {
      alert('请先生成完整提示')
      return
    }

    try {
      await window.api.clipboard.writeText(fullPrompt)
      alert('已复制到剪贴板')
    } catch (error) {
      alert(`复制失败: ${error}`)
    }
  }

  return (
    <div className="h-full flex flex-col">
      {/* 提示输入 */}
      <CyberCard className="flex-shrink-0 mb-4" title="LLM指令">
        <CyberInput
          placeholder="描述您希望执行的代码修改..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          className="mb-3"
        />
        
        <div className="flex gap-3">
          <CyberButton onClick={handleGeneratePrompt}>
            生成完整提示
          </CyberButton>
          <CyberButton variant="secondary" onClick={handleCopyPrompt}>
            复制到剪贴板
          </CyberButton>
        </div>
      </CyberCard>

      {/* 上下文预览 */}
      <CyberCard className="flex-1 flex flex-col min-h-0" title="生成的完整提示">
        <CyberTextarea
          value={fullPrompt}
          onChange={(e) => setFullPrompt(e.target.value)}
          placeholder="点击「生成完整提示」按钮生成..."
          className="flex-1 min-h-0"
        />
      </CyberCard>

      {/* 底部按钮 */}
      <div className="flex-shrink-0 flex justify-end gap-3 mt-4">
        <CyberButton variant="primary" onClick={onNext}>
          下一步: Diff预览
        </CyberButton>
      </div>
    </div>
  )
}

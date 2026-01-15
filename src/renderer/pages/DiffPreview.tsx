import React from 'react'
import { useDiffStore } from '../stores/diffStore'
import { CyberButton, CyberTextarea, CyberCard } from '../components/ui'
import { DiffViewer } from '../components/features'

interface DiffPreviewProps {
  onNext: () => void
}

export const DiffPreview: React.FC<DiffPreviewProps> = ({ onNext }) => {
  const {
    diffContent,
    setDiffContent,
    validationResult,
    setValidationResult,
    setParsedDiff,
    clearDiff
  } = useDiffStore()

  const handlePreview = async () => {
    if (!diffContent.trim()) {
      alert('请输入Diff内容')
      return
    }

    try {
      const result = await window.api.diff.parse(diffContent)
      if (result.success && result.data) {
        setParsedDiff(result.data)
      }
    } catch (error) {
      alert(`解析Diff失败: ${error}`)
    }
  }

  const handleValidate = async () => {
    if (!diffContent.trim()) {
      alert('请输入Diff内容')
      return
    }

    try {
      const result = await window.api.diff.validate(diffContent)
      setValidationResult(result)
      
      if (result.isValid) {
        if (result.warnings.length > 0) {
          alert(`格式验证通过，但有警告:\n${result.message}`)
        } else {
          alert('Diff格式验证通过')
        }
      } else {
        alert(`Diff格式验证失败:\n${result.message}`)
      }
    } catch (error) {
      alert(`验证失败: ${error}`)
    }
  }

  const handleClear = () => {
    clearDiff()
  }

  return (
    <div className="h-full flex flex-col">
      {/* 输入区域 */}
      <CyberCard className="flex-shrink-0 mb-4" title="粘贴LLM返回的Diff">
        <CyberTextarea
          value={diffContent}
          onChange={(e) => setDiffContent(e.target.value)}
          placeholder="在此粘贴LLM返回的diff内容..."
          className="h-32"
        />
        
        <div className="flex gap-3 mt-3">
          <CyberButton onClick={handlePreview}>
            预览Diff
          </CyberButton>
          <CyberButton variant="secondary" onClick={handleValidate}>
            验证格式
          </CyberButton>
          <CyberButton variant="ghost" onClick={handleClear}>
            清空
          </CyberButton>
        </div>

        {/* 验证结果 */}
        {validationResult && (
          <div className={`mt-3 p-3 rounded-md ${
            validationResult.isValid 
              ? 'bg-success-green/10 text-success-green' 
              : 'bg-error-red/10 text-error-red'
          }`}>
            {validationResult.message}
          </div>
        )}
      </CyberCard>

      {/* 预览区域 */}
      <CyberCard className="flex-1 flex flex-col min-h-0" title="Diff预览 (绿色=添加, 红色=删除)">
        <DiffViewer content={diffContent} className="flex-1 min-h-0" />
      </CyberCard>

      {/* 底部按钮 */}
      <div className="flex-shrink-0 flex justify-end gap-3 mt-4">
        <CyberButton 
          variant="primary" 
          onClick={onNext}
          disabled={!diffContent.trim()}
        >
          下一步: 应用代码
        </CyberButton>
      </div>
    </div>
  )
}

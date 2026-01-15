import React from 'react'
import { useProjectStore } from '../stores/projectStore'
import { useDiffStore } from '../stores/diffStore'
import { CyberButton, CyberCard, CyberCheckbox } from '../components/ui'
import { ProgressDialog } from '../components/features'

export const CodeApply: React.FC = () => {
  const { projectRoot } = useProjectStore()
  const {
    diffContent,
    parsedDiff,
    createBackup,
    setCreateBackup,
    dryRun,
    setDryRun,
    isApplying,
    setIsApplying,
    applyProgress,
    setApplyProgress,
    applyResult,
    setApplyResult
  } = useDiffStore()

  const handleApplyDiff = async () => {
    if (!diffContent.trim()) {
      alert('请先预览Diff内容')
      return
    }

    if (!projectRoot) {
      alert('请先选择项目根目录')
      return
    }

    // 验证 diff
    const validation = await window.api.diff.validate(diffContent)
    if (!validation.isValid) {
      alert(`Diff格式验证失败:\n${validation.message}`)
      return
    }

    if (validation.warnings.length > 0) {
      const proceed = confirm(`Diff验证有警告:\n${validation.message}\n\n是否继续？`)
      if (!proceed) return
    }

    // 解析 diff
    const parseResult = await window.api.diff.parse(diffContent)
    if (!parseResult.success || !parseResult.data || parseResult.data.length === 0) {
      alert('无法解析Diff内容或没有发现文件修改')
      return
    }

    const fileChanges = parseResult.data
    const affectedFiles = fileChanges.map((c: any) => c.newPath)

    // 确认对话框
    let confirmMsg = `即将修改以下 ${affectedFiles.length} 个文件:\n\n`
    confirmMsg += affectedFiles.slice(0, 10).map((p: string) => `• ${p}`).join('\n')
    if (affectedFiles.length > 10) {
      confirmMsg += `\n... 还有 ${affectedFiles.length - 10} 个文件`
    }
    confirmMsg += `\n\n备份: ${createBackup ? '是' : '否'}`
    confirmMsg += `\n预览模式: ${dryRun ? '是' : '否'}`
    confirmMsg += '\n\n确定要继续吗？'

    if (!confirm(confirmMsg)) return

    // 执行应用
    setIsApplying(true)
    setApplyProgress(0)

    try {
      setApplyProgress(30)
      
      const result = await window.api.diff.apply(diffContent, projectRoot, {
        createBackup,
        dryRun
      })

      setApplyProgress(100)
      setApplyResult(result)

      let resultMsg = `应用完成!\n\n成功: ${result.successCount} 个文件\n失败: ${result.errorCount} 个文件`
      if (dryRun) {
        resultMsg += '\n\n(预览模式，未实际修改文件)'
      } else if (result.backupDir) {
        resultMsg += `\n\n备份位置: ${result.backupDir}`
      }

      alert(resultMsg)
    } catch (error) {
      alert(`应用失败: ${error}`)
    } finally {
      setIsApplying(false)
    }
  }

  const handlePreviewChanges = async () => {
    if (!diffContent.trim()) {
      alert('请先预览Diff内容')
      return
    }

    try {
      const result = await window.api.diff.parse(diffContent)
      if (!result.success || !result.data || result.data.length === 0) {
        alert('没有发现文件修改')
        return
      }

      const fileChanges = result.data
      let previewContent = `将要修改的文件 (${fileChanges.length} 个):\n\n`

      fileChanges.forEach((change: any, i: number) => {
        previewContent += `${i + 1}. ${change.newPath}\n`
        previewContent += `   修改块数: ${change.hunks.length}\n`

        change.hunks.forEach((hunk: any, j: number) => {
          const additions = hunk.lines.filter((l: string) => l.startsWith('+')).length
          const deletions = hunk.lines.filter((l: string) => l.startsWith('-')).length
          previewContent += `   块 ${j + 1}: +${additions} -${deletions} 行\n`
        })

        previewContent += '\n'
      })

      alert(previewContent)
    } catch (error) {
      alert(`预览失败: ${error}`)
    }
  }

  return (
    <div className="h-full flex flex-col">
      {/* 说明信息 */}
      <CyberCard className="flex-shrink-0 mb-4">
        <div className="text-ghost-white">
          <p className="mb-2">两种应用方式：</p>
          <p className="text-cyber-gray text-sm">
            <strong className="text-neon-cyan">方式1 (推荐):</strong> 直接应用Diff - 自动解析并应用修改，支持备份和回滚
          </p>
          <p className="text-cyber-gray text-sm">
            <strong className="text-neon-cyan">方式2 (传统):</strong> 手动应用 - 生成提示给LLM，获取完整代码后手动替换
          </p>
        </div>
      </CyberCard>

      {/* 方式1: 直接应用 */}
      <CyberCard className="flex-shrink-0 mb-4" title="方式1: 直接应用Diff">
        <div className="flex items-center gap-6 mb-4">
          <CyberCheckbox
            checked={createBackup}
            onChange={setCreateBackup}
            label="创建备份文件"
          />
          <CyberCheckbox
            checked={dryRun}
            onChange={setDryRun}
            label="预览模式(不实际修改)"
          />
        </div>

        <div className="flex gap-3">
          <CyberButton variant="success" onClick={handleApplyDiff}>
            直接应用Diff
          </CyberButton>
          <CyberButton variant="secondary" onClick={handlePreviewChanges}>
            预览修改
          </CyberButton>
        </div>
      </CyberCard>

      {/* 应用结果 */}
      {applyResult && (
        <CyberCard className="flex-shrink-0 mb-4" title="应用结果">
          <div className="space-y-2">
            <div className="flex gap-4">
              <span className="text-success-green">
                成功: {applyResult.successCount} 个文件
              </span>
              <span className="text-error-red">
                失败: {applyResult.errorCount} 个文件
              </span>
            </div>
            
            {applyResult.backupDir && (
              <div className="text-cyber-gray text-sm">
                备份位置: {applyResult.backupDir}
              </div>
            )}

            {applyResult.errors.length > 0 && (
              <div className="mt-2">
                <div className="text-error-red text-sm mb-1">错误详情:</div>
                {applyResult.errors.map((err, i) => (
                  <div key={i} className="text-cyber-gray text-sm">• {err}</div>
                ))}
              </div>
            )}
          </div>
        </CyberCard>
      )}

      {/* 占位 */}
      <div className="flex-1" />

      {/* 进度对话框 */}
      <ProgressDialog
        isOpen={isApplying}
        title="应用Diff修改..."
        message="正在处理文件..."
        progress={applyProgress}
      />
    </div>
  )
}

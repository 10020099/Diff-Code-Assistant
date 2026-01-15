import React, { useState } from 'react'
import { useProjectStore } from '../stores/projectStore'
import { CyberButton, CyberInput, CyberCard, CyberCheckbox } from '../components/ui'
import { FileTree, StatsPanel, ProgressDialog } from '../components/features'

// 声明 window.api 类型
declare global {
  interface Window {
    api: {
      file: {
        scan: (rootDir: string, options?: { excludePatterns?: string[]; maxFileSize?: number }) => Promise<{ success: boolean; data?: any; error?: string }>
        generateContext: (files: any[], rootDir: string, includeLineNumbers?: boolean) => Promise<{ success: boolean; data?: string; error?: string }>
        getDefaultExcludePatterns: () => Promise<string[]>
        getSupportedExtensions: () => Promise<Record<string, string>>
      }
      diff: {
        validate: (diffContent: string) => Promise<any>
        parse: (diffContent: string) => Promise<any>
        apply: (diffContent: string, projectRoot: string, options?: { createBackup?: boolean; dryRun?: boolean }) => Promise<any>
        checkConflicts: (diffContent: string, projectRoot: string) => Promise<any>
      }
      backup: {
        list: (projectRoot: string) => Promise<any>
        rollback: (backupPath: string, projectRoot: string) => Promise<any>
        delete: (backupPath: string) => Promise<any>
        create: (filePaths: string[], projectRoot: string) => Promise<any>
      }
      dialog: {
        openDirectory: () => Promise<string | null>
      }
      clipboard: {
        writeText: (text: string) => Promise<void>
        readText: () => Promise<string>
      }
    }
  }
}

interface ProjectSetupProps {
  onNext: () => void
}

export const ProjectSetup: React.FC<ProjectSetupProps> = ({ onNext }) => {
  const {
    projectRoot,
    setProjectRoot,
    setScanResult,
    maxFileSize,
    setMaxFileSize,
    includeLineNumbers,
    setIncludeLineNumbers,
    isScanning,
    setIsScanning,
    scanProgress,
    setScanProgress,
    scanResult,
    selectedFiles,
    setContext
  } = useProjectStore()

  const [pathInput, setPathInput] = useState(projectRoot || '')

  const handleBrowse = async () => {
    const path = await window.api.dialog.openDirectory()
    if (path) {
      setPathInput(path)
      setProjectRoot(path)
    }
  }

  const handleScan = async () => {
    if (!pathInput) {
      alert('请选择项目目录')
      return
    }

    setProjectRoot(pathInput)
    setIsScanning(true)
    setScanProgress(0)

    try {
      setScanProgress(30)
      const result = await window.api.file.scan(pathInput, {
        maxFileSize: maxFileSize * 1024 * 1024
      })

      setScanProgress(70)

      if (result.success && result.data) {
        setScanResult(result.data)
        setScanProgress(100)
      } else {
        alert(`扫描失败: ${result.error}`)
      }
    } catch (error) {
      alert(`扫描出错: ${error}`)
    } finally {
      setIsScanning(false)
    }
  }

  const handleGenerateContext = async () => {
    if (!scanResult || !projectRoot) {
      alert('请先扫描项目')
      return
    }

    const selectedFilesData = scanResult.files.filter(f => selectedFiles.has(f.path))
    if (selectedFilesData.length === 0) {
      alert('请至少选择一个文件')
      return
    }

    setIsScanning(true)
    setScanProgress(50)

    try {
      const result = await window.api.file.generateContext(
        selectedFilesData,
        projectRoot,
        includeLineNumbers
      )

      if (result.success && result.data) {
        setContext(result.data)
        setScanProgress(100)
        onNext()
      } else {
        alert(`生成上下文失败: ${result.error}`)
      }
    } catch (error) {
      alert(`生成上下文出错: ${error}`)
    } finally {
      setIsScanning(false)
    }
  }

  return (
    <div className="h-full flex flex-col">
      {/* 顶部控制栏 */}
      <div className="flex-shrink-0 space-y-4 mb-4">
        {/* 路径选择 */}
        <div className="flex gap-3">
          <CyberInput
            placeholder="项目路径"
            value={pathInput}
            onChange={(e) => setPathInput(e.target.value)}
            className="flex-1"
          />
          <CyberButton onClick={handleBrowse}>
            浏览
          </CyberButton>
        </div>

        {/* 设置选项 */}
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <span className="text-sm text-cyber-gray">最大文件大小(MB):</span>
            <CyberInput
              type="number"
              value={maxFileSize}
              onChange={(e) => setMaxFileSize(Number(e.target.value) || 1)}
              className="w-20"
            />
          </div>

          <CyberCheckbox
            checked={includeLineNumbers}
            onChange={setIncludeLineNumbers}
            label="包含行号"
          />

          <CyberButton onClick={handleScan} loading={isScanning}>
            扫描项目
          </CyberButton>
        </div>
      </div>

      {/* 主内容区域 */}
      <div className="flex-1 flex gap-4 min-h-0">
        {/* 左侧：文件树 */}
        <CyberCard className="flex-1 flex flex-col" title="文件选择">
          <FileTree className="flex-1 min-h-0" />
        </CyberCard>

        {/* 右侧：统计信息 */}
        <div className="w-72 flex-shrink-0">
          <StatsPanel className="h-full" />
        </div>
      </div>

      {/* 底部按钮 */}
      <div className="flex-shrink-0 flex justify-end gap-3 mt-4">
        <CyberButton
          variant="primary"
          onClick={handleGenerateContext}
          disabled={!scanResult || selectedFiles.size === 0}
        >
          生成上下文
        </CyberButton>
      </div>

      {/* 进度对话框 */}
      <ProgressDialog
        isOpen={isScanning}
        title="处理中..."
        message={scanProgress < 50 ? '正在扫描文件...' : '正在生成上下文...'}
        progress={scanProgress}
      />
    </div>
  )
}

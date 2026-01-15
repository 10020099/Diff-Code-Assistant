import React from 'react'
import { useProjectStore } from '../../stores/projectStore'
import { CyberCard } from '../ui'
import { cn } from '../../utils/cn'

interface StatsPanelProps {
  className?: string
}

export const StatsPanel: React.FC<StatsPanelProps> = ({ className }) => {
  const { scanResult, selectedFiles } = useProjectStore()

  if (!scanResult) {
    return (
      <CyberCard className={className} title="项目统计">
        <div className="text-cyber-gray text-center py-4">
          请先扫描项目
        </div>
      </CyberCard>
    )
  }

  // 计算选中文件的统计
  const selectedFilesData = scanResult.files.filter(f => selectedFiles.has(f.path))
  const totalSize = selectedFilesData.reduce((sum, f) => sum + f.size, 0)
  
  // 统计文件类型
  const fileTypes: Record<string, number> = {}
  selectedFilesData.forEach(f => {
    fileTypes[f.extension] = (fileTypes[f.extension] || 0) + 1
  })
  
  const sortedTypes = Object.entries(fileTypes)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)

  const formatSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return (
    <CyberCard className={cn('h-full', className)} title="项目统计">
      <div className="space-y-4">
        {/* 基础统计 */}
        <div className="grid grid-cols-2 gap-3">
          <StatItem label="文件总数" value={selectedFilesData.length.toString()} />
          <StatItem label="总大小" value={formatSize(totalSize)} />
          <StatItem label="代码行数" value={scanResult.totalLines.toLocaleString()} />
          <StatItem label="文件类型" value={Object.keys(fileTypes).length.toString()} />
        </div>

        {/* 文件类型分布 */}
        {sortedTypes.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-cyber-gray mb-2">文件类型分布</h4>
            <div className="space-y-1">
              {sortedTypes.map(([ext, count]) => (
                <div key={ext} className="flex items-center justify-between text-sm">
                  <span className="text-ghost-white">{ext || '无扩展名'}</span>
                  <span className="text-neon-cyan">{count}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </CyberCard>
  )
}

interface StatItemProps {
  label: string
  value: string
}

const StatItem: React.FC<StatItemProps> = ({ label, value }) => (
  <div className="bg-dark-void rounded-md p-3">
    <div className="text-xs text-cyber-gray mb-1">{label}</div>
    <div className="text-lg font-semibold text-neon-cyan">{value}</div>
  </div>
)

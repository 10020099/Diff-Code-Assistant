import React, { useMemo, useState } from 'react'
import { useProjectStore, FileInfo } from '../../stores/projectStore'
import { CyberButton, CyberInput, CyberCheckbox } from '../ui'
import { cn } from '../../utils/cn'

interface FileTreeProps {
  className?: string
}

export const FileTree: React.FC<FileTreeProps> = ({ className }) => {
  const { 
    scanResult, 
    selectedFiles, 
    toggleFileSelection,
    selectAllFiles,
    deselectAllFiles,
    invertSelection
  } = useProjectStore()
  
  const [filter, setFilter] = useState('')

  const filteredFiles = useMemo(() => {
    if (!scanResult) return []
    if (!filter) return scanResult.files
    
    const lowerFilter = filter.toLowerCase()
    return scanResult.files.filter(f => 
      f.relativePath.toLowerCase().includes(lowerFilter) ||
      f.name.toLowerCase().includes(lowerFilter) ||
      f.type.toLowerCase().includes(lowerFilter)
    )
  }, [scanResult, filter])

  const selectedCount = selectedFiles.size
  const totalCount = scanResult?.files.length || 0

  if (!scanResult) {
    return (
      <div className={cn('flex items-center justify-center h-full text-cyber-gray', className)}>
        请先扫描项目目录
      </div>
    )
  }

  return (
    <div className={cn('flex flex-col h-full', className)}>
      {/* 搜索和控制栏 */}
      <div className="flex-shrink-0 space-y-2 mb-3">
        <CyberInput
          placeholder="输入关键词过滤文件..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          icon={
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          }
        />
        
        <div className="flex items-center gap-2">
          <CyberButton size="sm" variant="ghost" onClick={selectAllFiles}>
            全选
          </CyberButton>
          <CyberButton size="sm" variant="ghost" onClick={deselectAllFiles}>
            取消
          </CyberButton>
          <CyberButton size="sm" variant="ghost" onClick={invertSelection}>
            反选
          </CyberButton>
          <span className="ml-auto text-sm text-cyber-gray">
            选中: {selectedCount}/{totalCount}
          </span>
        </div>
      </div>

      {/* 文件列表 */}
      <div className="flex-1 overflow-auto">
        {filteredFiles.map((file) => (
          <FileTreeItem
            key={file.path}
            file={file}
            selected={selectedFiles.has(file.path)}
            onToggle={() => toggleFileSelection(file.path)}
          />
        ))}
        
        {filteredFiles.length === 0 && (
          <div className="text-center text-cyber-gray py-8">
            没有匹配的文件
          </div>
        )}
      </div>
    </div>
  )
}

interface FileTreeItemProps {
  file: FileInfo
  selected: boolean
  onToggle: () => void
}

const FileTreeItem: React.FC<FileTreeItemProps> = ({ file, selected, onToggle }) => {
  const indent = file.relativePath.split(/[/\\]/).length - 1

  return (
    <div
      className={cn(
        'flex items-center gap-2 px-2 py-1.5 rounded cursor-pointer transition-colors',
        'hover:bg-neon-cyan/10',
        selected && 'bg-neon-cyan/5'
      )}
      style={{ paddingLeft: `${8 + indent * 16}px` }}
      onClick={onToggle}
    >
      <CyberCheckbox
        checked={selected}
        onChange={onToggle}
      />
      
      <span className="flex-1 text-sm text-ghost-white truncate">
        {file.name}
      </span>
      
      <span className="text-xs text-cyber-gray">
        {file.sizeStr}
      </span>
      
      <span className="text-xs text-neon-purple px-1.5 py-0.5 bg-neon-purple/10 rounded">
        {file.type}
      </span>
    </div>
  )
}

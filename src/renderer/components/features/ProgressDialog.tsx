import React from 'react'
import { CyberProgress } from '../ui'
import { cn } from '../../utils/cn'

interface ProgressDialogProps {
  isOpen: boolean
  title: string
  message: string
  progress: number
  className?: string
}

export const ProgressDialog: React.FC<ProgressDialogProps> = ({
  isOpen,
  title,
  message,
  progress,
  className
}) => {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* 背景遮罩 */}
      <div className="absolute inset-0 bg-deep-space/80 backdrop-blur-sm" />
      
      {/* 对话框 */}
      <div
        className={cn(
          'relative bg-night-blue border-2 border-neon-cyan rounded-lg p-6 w-96',
          'shadow-[0_0_30px_rgba(0,243,255,0.3)]',
          className
        )}
      >
        <h3 className="text-lg font-semibold text-neon-cyan mb-4">{title}</h3>
        
        <p className="text-ghost-white mb-4">{message}</p>
        
        <CyberProgress value={progress} showLabel />
        
        {/* 装饰性角落 */}
        <div className="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-neon-cyan" />
        <div className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-neon-cyan" />
        <div className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-neon-cyan" />
        <div className="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-neon-cyan" />
      </div>
    </div>
  )
}

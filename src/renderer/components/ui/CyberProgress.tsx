import React from 'react'
import { cn } from '../../utils/cn'

interface CyberProgressProps {
  value: number // 0-100
  className?: string
  showLabel?: boolean
  variant?: 'default' | 'success' | 'warning' | 'error'
}

export const CyberProgress: React.FC<CyberProgressProps> = ({
  value,
  className,
  showLabel = false,
  variant = 'default'
}) => {
  const clampedValue = Math.min(100, Math.max(0, value))

  const variants = {
    default: 'from-neon-cyan to-neon-magenta',
    success: 'from-neon-green to-neon-cyan',
    warning: 'from-warning-orange to-neon-magenta',
    error: 'from-error-red to-neon-magenta'
  }

  return (
    <div className={cn('w-full', className)}>
      <div className="h-2 bg-shadow-gray rounded-full overflow-hidden">
        <div
          className={cn(
            'h-full bg-gradient-to-r rounded-full transition-all duration-300',
            variants[variant]
          )}
          style={{ width: `${clampedValue}%` }}
        />
      </div>
      {showLabel && (
        <div className="mt-1 text-sm text-cyber-gray text-right">
          {clampedValue.toFixed(0)}%
        </div>
      )}
    </div>
  )
}

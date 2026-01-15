import React from 'react'
import { cn } from '../../utils/cn'

interface CyberCardProps {
  children: React.ReactNode
  className?: string
  variant?: 'default' | 'highlight' | 'panel'
  title?: string
  actions?: React.ReactNode
}

export const CyberCard: React.FC<CyberCardProps> = ({
  children,
  className,
  variant = 'default',
  title,
  actions
}) => {
  const variants = {
    default: 'bg-night-blue border-shadow-gray hover:border-neon-cyan/50',
    highlight: 'bg-night-blue border-neon-cyan shadow-[0_0_10px_rgba(0,243,255,0.2)]',
    panel: 'bg-night-blue/50 border-neon-cyan/30'
  }

  return (
    <div
      className={cn(
        'border rounded-lg transition-all duration-300',
        variants[variant],
        className
      )}
    >
      {(title || actions) && (
        <div className="flex items-center justify-between px-4 py-3 border-b border-shadow-gray">
          {title && (
            <h3 className="text-lg font-semibold text-neon-cyan">{title}</h3>
          )}
          {actions && <div className="flex items-center gap-2">{actions}</div>}
        </div>
      )}
      <div className="p-4">{children}</div>
    </div>
  )
}

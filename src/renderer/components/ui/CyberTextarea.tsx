import React from 'react'
import { cn } from '../../utils/cn'

interface CyberTextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string
  error?: string
}

export const CyberTextarea: React.FC<CyberTextareaProps> = ({
  label,
  error,
  className,
  ...props
}) => {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-cyber-gray mb-1">
          {label}
        </label>
      )}
      <textarea
        className={cn(
          'w-full bg-night-blue border-2 border-shadow-gray rounded-md px-4 py-3',
          'text-ghost-white placeholder-cyber-gray font-mono text-sm',
          'focus:outline-none focus:border-neon-cyan focus:shadow-[0_0_10px_rgba(0,243,255,0.2)]',
          'transition-all duration-200 resize-y min-h-[100px]',
          error && 'border-error-red focus:border-error-red',
          className
        )}
        {...props}
      />
      {error && (
        <p className="mt-1 text-sm text-error-red">{error}</p>
      )}
    </div>
  )
}

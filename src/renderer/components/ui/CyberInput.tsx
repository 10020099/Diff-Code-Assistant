import React from 'react'
import { cn } from '../../utils/cn'

interface CyberInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  icon?: React.ReactNode
}

export const CyberInput: React.FC<CyberInputProps> = ({
  label,
  error,
  icon,
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
      <div className="relative">
        {icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-cyber-gray">
            {icon}
          </div>
        )}
        <input
          className={cn(
            'w-full bg-night-blue border-2 border-shadow-gray rounded-md px-4 py-2.5',
            'text-ghost-white placeholder-cyber-gray',
            'focus:outline-none focus:border-neon-cyan focus:shadow-[0_0_10px_rgba(0,243,255,0.2)]',
            'transition-all duration-200',
            icon && 'pl-10',
            error && 'border-error-red focus:border-error-red',
            className
          )}
          {...props}
        />
      </div>
      {error && (
        <p className="mt-1 text-sm text-error-red">{error}</p>
      )}
    </div>
  )
}

import React from 'react'
import { cn } from '../../utils/cn'

interface CyberCheckboxProps {
  checked: boolean
  onChange: (checked: boolean) => void
  label?: string
  disabled?: boolean
  className?: string
}

export const CyberCheckbox: React.FC<CyberCheckboxProps> = ({
  checked,
  onChange,
  label,
  disabled = false,
  className
}) => {
  return (
    <label
      className={cn(
        'inline-flex items-center gap-2 cursor-pointer select-none',
        disabled && 'opacity-50 cursor-not-allowed',
        className
      )}
    >
      <div className="relative">
        <input
          type="checkbox"
          checked={checked}
          onChange={(e) => !disabled && onChange(e.target.checked)}
          disabled={disabled}
          className="sr-only"
        />
        <div
          className={cn(
            'w-5 h-5 border-2 rounded transition-all duration-200',
            checked
              ? 'bg-neon-purple border-neon-purple'
              : 'bg-transparent border-shadow-gray hover:border-neon-cyan'
          )}
        >
          {checked && (
            <svg
              className="w-full h-full text-ghost-white p-0.5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={3}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          )}
        </div>
      </div>
      {label && <span className="text-sm text-ghost-white">{label}</span>}
    </label>
  )
}

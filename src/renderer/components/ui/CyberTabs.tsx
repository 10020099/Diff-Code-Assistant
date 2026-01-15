import React from 'react'
import { cn } from '../../utils/cn'

interface CyberTabsProps {
  tabs: Array<{
    id: string
    label: string
    icon?: React.ReactNode
  }>
  activeTab: string
  onChange: (tabId: string) => void
  className?: string
}

export const CyberTabs: React.FC<CyberTabsProps> = ({
  tabs,
  activeTab,
  onChange,
  className
}) => {
  return (
    <div className={cn('flex gap-1 bg-dark-void p-1 rounded-lg', className)}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={cn(
            'flex items-center gap-2 px-4 py-2.5 rounded-md font-medium transition-all duration-200',
            activeTab === tab.id
              ? 'bg-neon-cyan text-deep-space'
              : 'text-cyber-gray hover:text-ghost-white hover:bg-neon-cyan/10'
          )}
        >
          {tab.icon}
          {tab.label}
        </button>
      ))}
    </div>
  )
}

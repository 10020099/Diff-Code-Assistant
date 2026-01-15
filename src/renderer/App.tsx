import React, { useState } from 'react'
import { CyberTabs } from './components/ui'
import { ScanlineOverlay } from './components/effects'
import { ProjectSetup, ContextGeneration, DiffPreview, CodeApply } from './pages'

const TABS = [
  { id: 'project', label: '项目设置' },
  { id: 'context', label: '上下文生成' },
  { id: 'diff', label: 'Diff预览' },
  { id: 'apply', label: '代码应用' }
]

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('project')

  const goToTab = (tabId: string) => {
    setActiveTab(tabId)
  }

  return (
    <div className="h-screen flex flex-col bg-deep-space">
      {/* 扫描线特效 */}
      <ScanlineOverlay opacity={0.05} />

      {/* 标题栏 */}
      <header className="flex-shrink-0 px-6 py-4 border-b border-shadow-gray">
        <h1 className="text-2xl font-bold text-center">
          <span className="text-neon-cyan neon-glow">DIFF CODE ASSISTANT</span>
          <span className="text-cyber-gray text-sm ml-3">- CYBERPUNK ENHANCED -</span>
        </h1>
      </header>

      {/* 标签页导航 */}
      <nav className="flex-shrink-0 px-6 py-3">
        <CyberTabs
          tabs={TABS}
          activeTab={activeTab}
          onChange={setActiveTab}
        />
      </nav>

      {/* 主内容区域 */}
      <main className="flex-1 px-6 pb-6 min-h-0">
        <div className="h-full">
          {activeTab === 'project' && (
            <ProjectSetup onNext={() => goToTab('context')} />
          )}
          {activeTab === 'context' && (
            <ContextGeneration onNext={() => goToTab('diff')} />
          )}
          {activeTab === 'diff' && (
            <DiffPreview onNext={() => goToTab('apply')} />
          )}
          {activeTab === 'apply' && (
            <CodeApply />
          )}
        </div>
      </main>

      {/* 装饰性角落 */}
      <div className="fixed top-0 left-0 w-8 h-8 border-t-2 border-l-2 border-neon-cyan/50 pointer-events-none" />
      <div className="fixed top-0 right-0 w-8 h-8 border-t-2 border-r-2 border-neon-cyan/50 pointer-events-none" />
      <div className="fixed bottom-0 left-0 w-8 h-8 border-b-2 border-l-2 border-neon-cyan/50 pointer-events-none" />
      <div className="fixed bottom-0 right-0 w-8 h-8 border-b-2 border-r-2 border-neon-cyan/50 pointer-events-none" />
    </div>
  )
}

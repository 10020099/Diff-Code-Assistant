import { create } from 'zustand'

export interface DiffHunk {
  oldStart: number
  oldCount: number
  newStart: number
  newCount: number
  lines: string[]
}

export interface FileChange {
  oldPath: string
  newPath: string
  hunks: DiffHunk[]
  isNewFile: boolean
  isDeletedFile: boolean
}

export interface DiffValidationResult {
  isValid: boolean
  message: string
  warnings: string[]
  errors: string[]
}

interface DiffState {
  // Diff 状态
  diffContent: string
  parsedDiff: FileChange[]
  validationResult: DiffValidationResult | null
  
  // 应用状态
  isApplying: boolean
  applyProgress: number
  applyResult: {
    success: boolean
    successCount: number
    errorCount: number
    errors: string[]
    backupDir?: string
  } | null
  
  // 设置
  createBackup: boolean
  dryRun: boolean
  
  // Actions
  setDiffContent: (content: string) => void
  setParsedDiff: (diff: FileChange[]) => void
  setValidationResult: (result: DiffValidationResult | null) => void
  setIsApplying: (applying: boolean) => void
  setApplyProgress: (progress: number) => void
  setApplyResult: (result: DiffState['applyResult']) => void
  setCreateBackup: (create: boolean) => void
  setDryRun: (dryRun: boolean) => void
  clearDiff: () => void
  reset: () => void
}

const initialState = {
  diffContent: '',
  parsedDiff: [],
  validationResult: null,
  isApplying: false,
  applyProgress: 0,
  applyResult: null,
  createBackup: true,
  dryRun: false
}

export const useDiffStore = create<DiffState>((set) => ({
  ...initialState,

  setDiffContent: (content) => set({ diffContent: content }),
  setParsedDiff: (diff) => set({ parsedDiff: diff }),
  setValidationResult: (result) => set({ validationResult: result }),
  setIsApplying: (applying) => set({ isApplying: applying }),
  setApplyProgress: (progress) => set({ applyProgress: progress }),
  setApplyResult: (result) => set({ applyResult: result }),
  setCreateBackup: (create) => set({ createBackup: create }),
  setDryRun: (dryRun) => set({ dryRun: dryRun }),
  
  clearDiff: () => set({
    diffContent: '',
    parsedDiff: [],
    validationResult: null,
    applyResult: null
  }),
  
  reset: () => set(initialState)
}))

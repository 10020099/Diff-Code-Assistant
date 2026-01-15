import { create } from 'zustand'

export interface FileInfo {
  path: string
  relativePath: string
  name: string
  extension: string
  size: number
  sizeStr: string
  type: string
  isText: boolean
}

export interface ScanResult {
  files: FileInfo[]
  totalFiles: number
  totalSize: number
  totalLines: number
  fileTypes: Record<string, number>
}

interface ProjectState {
  // 项目状态
  projectRoot: string | null
  scanResult: ScanResult | null
  selectedFiles: Set<string>
  context: string
  isScanning: boolean
  scanProgress: number
  
  // 设置
  maxFileSize: number
  includeLineNumbers: boolean
  excludePatterns: string[]
  
  // Actions
  setProjectRoot: (path: string | null) => void
  setScanResult: (result: ScanResult | null) => void
  setSelectedFiles: (files: Set<string>) => void
  toggleFileSelection: (filePath: string) => void
  selectAllFiles: () => void
  deselectAllFiles: () => void
  invertSelection: () => void
  setContext: (context: string) => void
  setIsScanning: (scanning: boolean) => void
  setScanProgress: (progress: number) => void
  setMaxFileSize: (size: number) => void
  setIncludeLineNumbers: (include: boolean) => void
  setExcludePatterns: (patterns: string[]) => void
  reset: () => void
}

const initialState = {
  projectRoot: null,
  scanResult: null,
  selectedFiles: new Set<string>(),
  context: '',
  isScanning: false,
  scanProgress: 0,
  maxFileSize: 1,
  includeLineNumbers: true,
  excludePatterns: []
}

export const useProjectStore = create<ProjectState>((set, get) => ({
  ...initialState,

  setProjectRoot: (path) => set({ projectRoot: path }),
  
  setScanResult: (result) => {
    if (result) {
      // 默认选中所有文件
      const selectedFiles = new Set(result.files.map(f => f.path))
      set({ scanResult: result, selectedFiles })
    } else {
      set({ scanResult: result, selectedFiles: new Set() })
    }
  },
  
  setSelectedFiles: (files) => set({ selectedFiles: files }),
  
  toggleFileSelection: (filePath) => {
    const { selectedFiles } = get()
    const newSelected = new Set(selectedFiles)
    if (newSelected.has(filePath)) {
      newSelected.delete(filePath)
    } else {
      newSelected.add(filePath)
    }
    set({ selectedFiles: newSelected })
  },
  
  selectAllFiles: () => {
    const { scanResult } = get()
    if (scanResult) {
      set({ selectedFiles: new Set(scanResult.files.map(f => f.path)) })
    }
  },
  
  deselectAllFiles: () => set({ selectedFiles: new Set() }),
  
  invertSelection: () => {
    const { scanResult, selectedFiles } = get()
    if (scanResult) {
      const newSelected = new Set<string>()
      scanResult.files.forEach(f => {
        if (!selectedFiles.has(f.path)) {
          newSelected.add(f.path)
        }
      })
      set({ selectedFiles: newSelected })
    }
  },
  
  setContext: (context) => set({ context }),
  setIsScanning: (scanning) => set({ isScanning: scanning }),
  setScanProgress: (progress) => set({ scanProgress: progress }),
  setMaxFileSize: (size) => set({ maxFileSize: size }),
  setIncludeLineNumbers: (include) => set({ includeLineNumbers: include }),
  setExcludePatterns: (patterns) => set({ excludePatterns: patterns }),
  
  reset: () => set(initialState)
}))

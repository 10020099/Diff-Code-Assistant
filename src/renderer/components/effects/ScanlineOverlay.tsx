import React from 'react'

interface ScanlineOverlayProps {
  opacity?: number
  speed?: number
}

export const ScanlineOverlay: React.FC<ScanlineOverlayProps> = ({
  opacity = 0.1,
  speed = 8
}) => {
  return (
    <div 
      className="fixed inset-0 pointer-events-none z-[9999] overflow-hidden"
      style={{ opacity }}
    >
      <div
        className="absolute w-full h-1 bg-gradient-to-b from-transparent via-neon-cyan/30 to-transparent"
        style={{
          animation: `scanline ${speed}s linear infinite`
        }}
      />
    </div>
  )
}

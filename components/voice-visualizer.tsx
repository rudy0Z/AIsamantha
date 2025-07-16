"use client"

import { useEffect, useState } from "react"

export function VoiceVisualizer() {
  const [bars, setBars] = useState<number[]>(new Array(20).fill(0))

  useEffect(() => {
    const interval = setInterval(() => {
      setBars((prev) => prev.map(() => Math.random() * 100))
    }, 100)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="flex items-center justify-center gap-1 mt-4 h-16">
      {bars.map((height, index) => (
        <div
          key={index}
          className="bg-rose-400 rounded-full transition-all duration-100 ease-out"
          style={{
            width: "3px",
            height: `${Math.max(height * 0.6, 10)}%`,
            opacity: 0.7 + (height / 100) * 0.3,
          }}
        />
      ))}
    </div>
  )
}

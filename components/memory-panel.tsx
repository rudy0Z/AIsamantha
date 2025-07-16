"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Brain, ChevronDown, ChevronUp, Calendar, Clock } from "lucide-react"

interface Memory {
  timestamp: string
  userInput: string
  aiResponse: string
  emotion: any
  context: {
    timeOfDay: number
    dayOfWeek: number
  }
}

interface MemoryPanelProps {
  isOpen: boolean
  onToggle: () => void
}

export function MemoryPanel({ isOpen, onToggle }: MemoryPanelProps) {
  const [memories, setMemories] = useState<Memory[]>([])
  const [selectedMemory, setSelectedMemory] = useState<Memory | null>(null)

  useEffect(() => {
    const loadMemories = () => {
      const stored = localStorage.getItem("samantha-memories")
      if (stored) {
        const parsed = JSON.parse(stored)
        setMemories(parsed.slice(-10).reverse()) // Show last 10, most recent first
      }
    }

    loadMemories()

    // Refresh memories when panel opens
    if (isOpen) {
      loadMemories()
    }
  }, [isOpen])

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    })
  }

  const getEmotionSummary = (emotion: any) => {
    if (!emotion) return "neutral"
    return `${emotion.sentiment} (${emotion.intensity}/10)`
  }

  return (
    <Card className="bg-white/70 backdrop-blur-sm border-rose-200">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Brain className="w-5 h-5 text-purple-500" />
            Memory Bank
          </CardTitle>
          <Button variant="ghost" size="sm" onClick={onToggle} className="p-1">
            {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </Button>
        </div>
      </CardHeader>

      {isOpen && (
        <CardContent className="space-y-3 max-h-96 overflow-y-auto">
          {memories.length === 0 ? (
            <p className="text-sm text-gray-500">No memories yet. Start a conversation!</p>
          ) : (
            <>
              <div className="space-y-2">
                {memories.map((memory, index) => (
                  <div
                    key={index}
                    className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                      selectedMemory === memory
                        ? "bg-rose-50 border-rose-300"
                        : "bg-gray-50 border-gray-200 hover:bg-gray-100"
                    }`}
                    onClick={() => setSelectedMemory(selectedMemory === memory ? null : memory)}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        <Clock className="w-3 h-3" />
                        {formatTime(memory.timestamp)}
                      </div>
                      <span className="text-xs px-2 py-1 bg-purple-100 text-purple-700 rounded-full">
                        {getEmotionSummary(memory.emotion)}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 truncate">
                      {memory.userInput.replace(/\[.*?\]\n\nUser said: "/, "").replace(/"$/, "")}
                    </p>
                  </div>
                ))}
              </div>

              {selectedMemory && (
                <div className="mt-4 p-4 bg-white rounded-lg border border-rose-200">
                  <div className="space-y-3">
                    <div>
                      <h4 className="text-sm font-medium text-gray-800 mb-1">You said:</h4>
                      <p className="text-sm text-gray-600">
                        {selectedMemory.userInput.replace(/\[.*?\]\n\nUser said: "/, "").replace(/"$/, "")}
                      </p>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-gray-800 mb-1">I responded:</h4>
                      <p className="text-sm text-gray-600">{selectedMemory.aiResponse}</p>
                    </div>
                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <div className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {formatTime(selectedMemory.timestamp)}
                      </div>
                      {selectedMemory.emotion && (
                        <div>
                          Mood: {selectedMemory.emotion.sentiment} ({selectedMemory.emotion.intensity}/10)
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      )}
    </Card>
  )
}

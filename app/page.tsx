"use client"

import { useState, useEffect, useRef } from "react"
import { useChat } from "ai/react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Mic, MicOff, Volume2, VolumeX, Heart, Brain } from "lucide-react"
import { EmotionDetector } from "@/components/emotion-detector"
import { VoiceVisualizer } from "@/components/voice-visualizer"
import { MemoryPanel } from "@/components/memory-panel"
import type { SpeechRecognition } from "web-speech-api"

interface EmotionState {
  sentiment: "positive" | "negative" | "neutral"
  emotions: string[]
  intensity: number
}

export default function SamanthaAI() {
  const [isListening, setIsListening] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [transcript, setTranscript] = useState("")
  const [currentEmotion, setCurrentEmotion] = useState<EmotionState | null>(null)
  const [voiceEnabled, setVoiceEnabled] = useState(true)
  const [showMemory, setShowMemory] = useState(false)

  const recognitionRef = useRef<SpeechRecognition | null>(null)
  const synthRef = useRef<SpeechSynthesis | null>(null)

  const { messages, append, isLoading } = useChat({
    api: "/api/chat",
    onFinish: (message) => {
      if (voiceEnabled && message.content) {
        speakResponse(message.content)
      }
      // Save conversation to memory
      saveToMemory(transcript, message.content, currentEmotion)
    },
  })

  useEffect(() => {
    if (typeof window !== "undefined") {
      synthRef.current = window.speechSynthesis

      if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
        recognitionRef.current = new SpeechRecognition()
        recognitionRef.current.continuous = false
        recognitionRef.current.interimResults = false
        recognitionRef.current.lang = "en-US"

        recognitionRef.current.onresult = (event) => {
          const result = event.results[0][0].transcript
          setTranscript(result)
          handleVoiceInput(result)
        }

        recognitionRef.current.onend = () => {
          setIsListening(false)
        }
      }
    }
  }, [])

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      setIsListening(true)
      recognitionRef.current.start()
    }
  }

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop()
      setIsListening(false)
    }
  }

  const handleVoiceInput = async (text: string) => {
    // Detect emotion from the text
    const emotion = await detectEmotion(text)
    setCurrentEmotion(emotion)

    // Send to AI with emotional context
    const emotionalContext = emotion
      ? `[User seems ${emotion.sentiment} with emotions: ${emotion.emotions.join(", ")}. Intensity: ${emotion.intensity}/10]`
      : ""

    await append({
      role: "user",
      content: `${emotionalContext}\n\nUser said: "${text}"`,
    })
  }

  const speakResponse = (text: string) => {
    if (synthRef.current && voiceEnabled) {
      // Stop any current speech
      synthRef.current.cancel()

      const utterance = new SpeechSynthesisUtterance(text)

      // Configure voice for emotional intelligence
      const voices = synthRef.current.getVoices()
      const femaleVoice =
        voices.find(
          (voice) => voice.name.includes("Female") || voice.name.includes("Samantha") || voice.gender === "female",
        ) || voices.find((voice) => voice.lang.startsWith("en"))

      if (femaleVoice) {
        utterance.voice = femaleVoice
      }

      // Adjust speech based on detected emotion and time
      const hour = new Date().getHours()
      if (hour >= 22 || hour <= 6) {
        // Night mode - softer, slower
        utterance.rate = 0.8
        utterance.pitch = 0.9
        utterance.volume = 0.7
      } else if (currentEmotion?.sentiment === "negative") {
        // Compassionate tone
        utterance.rate = 0.9
        utterance.pitch = 0.95
        utterance.volume = 0.8
      } else if (currentEmotion?.sentiment === "positive") {
        // Cheerful tone
        utterance.rate = 1.1
        utterance.pitch = 1.05
        utterance.volume = 0.9
      }

      utterance.onstart = () => setIsSpeaking(true)
      utterance.onend = () => setIsSpeaking(false)

      synthRef.current.speak(utterance)
    }
  }

  const detectEmotion = async (text: string): Promise<EmotionState> => {
    try {
      const response = await fetch("/api/emotion", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      })
      return await response.json()
    } catch (error) {
      console.error("Emotion detection failed:", error)
      return { sentiment: "neutral", emotions: [], intensity: 5 }
    }
  }

  const saveToMemory = (userInput: string, aiResponse: string, emotion: EmotionState | null) => {
    const memory = {
      timestamp: new Date().toISOString(),
      userInput,
      aiResponse,
      emotion,
      context: {
        timeOfDay: new Date().getHours(),
        dayOfWeek: new Date().getDay(),
      },
    }

    const existingMemories = JSON.parse(localStorage.getItem("samantha-memories") || "[]")
    existingMemories.push(memory)

    // Keep only last 100 conversations
    if (existingMemories.length > 100) {
      existingMemories.splice(0, existingMemories.length - 100)
    }

    localStorage.setItem("samantha-memories", JSON.stringify(existingMemories))
  }

  const getGreeting = () => {
    const hour = new Date().getHours()
    const memories = JSON.parse(localStorage.getItem("samantha-memories") || "[]")
    const hasHistory = memories.length > 0

    if (hour < 12) {
      return hasHistory
        ? "Good morning! How are you feeling today?"
        : "Good morning! I'm Samantha. I'm here to listen and understand."
    } else if (hour < 18) {
      return hasHistory
        ? "Good afternoon! What's on your mind?"
        : "Hello! I'm Samantha, your AI companion. I'm here to listen."
    } else {
      return hasHistory
        ? "Good evening! How was your day?"
        : "Good evening! I'm Samantha. I'm here to be your thoughtful companion."
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-rose-50 via-white to-orange-50 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Heart className="w-8 h-8 text-rose-500" />
            <h1 className="text-4xl font-light text-gray-800">Samantha</h1>
            <Brain className="w-8 h-8 text-rose-500" />
          </div>
          <p className="text-gray-600 text-lg font-light">Your emotionally intelligent AI companion</p>
        </div>

        {/* Main Interface */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Conversation Area */}
          <div className="lg:col-span-2">
            <Card className="h-[600px] flex flex-col bg-white/70 backdrop-blur-sm border-rose-200">
              <CardContent className="flex-1 p-6 overflow-y-auto">
                {messages.length === 0 ? (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                      <div className="text-6xl mb-4">🎧</div>
                      <p className="text-gray-600 text-lg mb-4">{getGreeting()}</p>
                      <p className="text-gray-500">Press the microphone to start talking</p>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {messages.map((message, index) => (
                      <div key={index} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                        <div
                          className={`max-w-[80%] p-4 rounded-2xl ${
                            message.role === "user" ? "bg-rose-500 text-white" : "bg-gray-100 text-gray-800"
                          }`}
                        >
                          {message.content.replace(/\[.*?\]\n\n/, "")}
                        </div>
                      </div>
                    ))}
                    {isLoading && (
                      <div className="flex justify-start">
                        <div className="bg-gray-100 text-gray-800 p-4 rounded-2xl">
                          <div className="flex items-center gap-2">
                            <div className="w-2 h-2 bg-rose-400 rounded-full animate-bounce"></div>
                            <div
                              className="w-2 h-2 bg-rose-400 rounded-full animate-bounce"
                              style={{ animationDelay: "0.1s" }}
                            ></div>
                            <div
                              className="w-2 h-2 bg-rose-400 rounded-full animate-bounce"
                              style={{ animationDelay: "0.2s" }}
                            ></div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>

              {/* Voice Controls */}
              <div className="p-6 border-t border-rose-200">
                <div className="flex items-center justify-center gap-4">
                  <Button
                    onClick={isListening ? stopListening : startListening}
                    disabled={isLoading || isSpeaking}
                    size="lg"
                    className={`rounded-full w-16 h-16 ${
                      isListening ? "bg-red-500 hover:bg-red-600 animate-pulse" : "bg-rose-500 hover:bg-rose-600"
                    }`}
                  >
                    {isListening ? <MicOff className="w-6 h-6" /> : <Mic className="w-6 h-6" />}
                  </Button>

                  <Button
                    onClick={() => setVoiceEnabled(!voiceEnabled)}
                    variant="outline"
                    size="lg"
                    className="rounded-full w-12 h-12"
                  >
                    {voiceEnabled ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
                  </Button>
                </div>

                {isListening && <VoiceVisualizer />}

                {transcript && (
                  <div className="mt-4 p-3 bg-rose-50 rounded-lg">
                    <p className="text-sm text-gray-600">Last heard: "{transcript}"</p>
                  </div>
                )}
              </div>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Emotion Display */}
            <EmotionDetector emotion={currentEmotion} />

            {/* Memory Panel */}
            <MemoryPanel isOpen={showMemory} onToggle={() => setShowMemory(!showMemory)} />

            {/* Status */}
            <Card className="bg-white/70 backdrop-blur-sm border-rose-200">
              <CardContent className="p-4">
                <h3 className="font-medium text-gray-800 mb-3">Status</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Listening:</span>
                    <span className={isListening ? "text-green-600" : "text-gray-500"}>
                      {isListening ? "Active" : "Inactive"}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Speaking:</span>
                    <span className={isSpeaking ? "text-blue-600" : "text-gray-500"}>
                      {isSpeaking ? "Active" : "Inactive"}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Voice Output:</span>
                    <span className={voiceEnabled ? "text-green-600" : "text-gray-500"}>
                      {voiceEnabled ? "Enabled" : "Disabled"}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

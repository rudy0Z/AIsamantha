import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Heart, Smile, Frown, Meh } from "lucide-react"

interface EmotionState {
  sentiment: "positive" | "negative" | "neutral"
  emotions: string[]
  intensity: number
}

interface EmotionDetectorProps {
  emotion: EmotionState | null
}

export function EmotionDetector({ emotion }: EmotionDetectorProps) {
  const getEmotionIcon = () => {
    if (!emotion) return <Heart className="w-5 h-5 text-gray-400" />

    switch (emotion.sentiment) {
      case "positive":
        return <Smile className="w-5 h-5 text-green-500" />
      case "negative":
        return <Frown className="w-5 h-5 text-red-500" />
      default:
        return <Meh className="w-5 h-5 text-yellow-500" />
    }
  }

  const getIntensityColor = (intensity: number) => {
    if (intensity >= 8) return "bg-red-500"
    if (intensity >= 6) return "bg-orange-500"
    if (intensity >= 4) return "bg-yellow-500"
    return "bg-green-500"
  }

  return (
    <Card className="bg-white/70 backdrop-blur-sm border-rose-200">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg flex items-center gap-2">
          {getEmotionIcon()}
          Emotional State
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {emotion ? (
          <>
            <div>
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm font-medium">Sentiment</span>
                <span
                  className={`text-sm px-2 py-1 rounded-full ${
                    emotion.sentiment === "positive"
                      ? "bg-green-100 text-green-800"
                      : emotion.sentiment === "negative"
                        ? "bg-red-100 text-red-800"
                        : "bg-gray-100 text-gray-800"
                  }`}
                >
                  {emotion.sentiment}
                </span>
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium">Intensity</span>
                <span className="text-sm">{emotion.intensity}/10</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-300 ${getIntensityColor(emotion.intensity)}`}
                  style={{ width: `${emotion.intensity * 10}%` }}
                ></div>
              </div>
            </div>

            {emotion.emotions.length > 0 && (
              <div>
                <span className="text-sm font-medium block mb-2">Detected Emotions</span>
                <div className="flex flex-wrap gap-1">
                  {emotion.emotions.map((emo, index) => (
                    <span key={index} className="text-xs px-2 py-1 bg-rose-100 text-rose-800 rounded-full">
                      {emo}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </>
        ) : (
          <p className="text-sm text-gray-500">Start talking to detect emotions...</p>
        )}
      </CardContent>
    </Card>
  )
}

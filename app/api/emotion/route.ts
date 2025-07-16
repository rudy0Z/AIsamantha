import { NextResponse } from "next/server"

// Simple emotion detection based on keywords and patterns
const emotionKeywords = {
  joy: ["happy", "excited", "thrilled", "delighted", "cheerful", "elated", "joyful", "glad", "pleased"],
  sadness: ["sad", "depressed", "down", "upset", "disappointed", "heartbroken", "miserable", "gloomy"],
  anger: ["angry", "furious", "mad", "irritated", "annoyed", "frustrated", "outraged", "livid"],
  fear: ["scared", "afraid", "terrified", "anxious", "worried", "nervous", "frightened", "panicked"],
  surprise: ["surprised", "shocked", "amazed", "astonished", "stunned", "bewildered"],
  disgust: ["disgusted", "revolted", "repulsed", "sickened", "appalled"],
  love: ["love", "adore", "cherish", "treasure", "devoted", "affectionate"],
  hope: ["hopeful", "optimistic", "confident", "positive", "encouraged"],
  loneliness: ["lonely", "isolated", "alone", "abandoned", "disconnected"],
  stress: ["stressed", "overwhelmed", "pressured", "tense", "strained"],
}

const positiveWords = [
  "good",
  "great",
  "awesome",
  "wonderful",
  "amazing",
  "fantastic",
  "excellent",
  "perfect",
  "beautiful",
  "lovely",
]
const negativeWords = [
  "bad",
  "terrible",
  "awful",
  "horrible",
  "disgusting",
  "hate",
  "worst",
  "stupid",
  "annoying",
  "frustrating",
]

export async function POST(req: Request) {
  try {
    const { text } = await req.json()

    if (!text) {
      return NextResponse.json({
        sentiment: "neutral",
        emotions: [],
        intensity: 5,
      })
    }

    const lowerText = text.toLowerCase()
    const words = lowerText.split(/\s+/)

    // Detect emotions
    const detectedEmotions: string[] = []
    let emotionScore = 0

    Object.entries(emotionKeywords).forEach(([emotion, keywords]) => {
      const matches = keywords.filter((keyword) => lowerText.includes(keyword))
      if (matches.length > 0) {
        detectedEmotions.push(emotion)
        emotionScore += matches.length
      }
    })

    // Calculate sentiment
    const positiveMatches = positiveWords.filter((word) => lowerText.includes(word)).length
    const negativeMatches = negativeWords.filter((word) => lowerText.includes(word)).length

    let sentiment: "positive" | "negative" | "neutral" = "neutral"
    if (positiveMatches > negativeMatches) {
      sentiment = "positive"
    } else if (negativeMatches > positiveMatches) {
      sentiment = "negative"
    }

    // Calculate intensity (1-10)
    const totalMatches = positiveMatches + negativeMatches + emotionScore
    const intensity = Math.min(Math.max(Math.round((totalMatches / words.length) * 50 + 5), 1), 10)

    // Adjust sentiment based on detected emotions
    const positiveEmotions = ["joy", "love", "hope"]
    const negativeEmotions = ["sadness", "anger", "fear", "disgust", "loneliness", "stress"]

    const hasPositiveEmotions = detectedEmotions.some((e) => positiveEmotions.includes(e))
    const hasNegativeEmotions = detectedEmotions.some((e) => negativeEmotions.includes(e))

    if (hasPositiveEmotions && !hasNegativeEmotions) {
      sentiment = "positive"
    } else if (hasNegativeEmotions && !hasPositiveEmotions) {
      sentiment = "negative"
    }

    return NextResponse.json({
      sentiment,
      emotions: detectedEmotions,
      intensity,
    })
  } catch (error) {
    console.error("Emotion detection error:", error)
    return NextResponse.json({
      sentiment: "neutral",
      emotions: [],
      intensity: 5,
    })
  }
}

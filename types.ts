
export type Sender = 'user' | 'ai';

export const Emotions = ['happy', 'sad', 'angry', 'curious', 'neutral', 'excited'] as const;

export type Emotion = typeof Emotions[number];

export type MessageType = 'standard' | 'reflection';

export interface Message {
  id: string;
  sender: Sender;
  text: string;
  emotion?: Emotion;
  type?: MessageType;
}

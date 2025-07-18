
import type { Emotion, Message, MessageType } from '../types.ts';

interface ApiResponse {
  response: string;
  emotion: Emotion;
  type: MessageType;
}

interface ReflectionAnswer {
  question: string;
}

/**
 * Posts a message to the secure backend service, which then communicates with the Gemini API.
 * @param message The user's most recent message.
 * @param history The entire conversation history for context.
 * @param reflectionAnswer Optional context if the user is answering a reflection question.
 * @returns A promise that resolves to an object containing the AI's response, emotion, and type.
 */
export const postChatMessage = async (
  message: string,
  history: Message[],
  reflectionAnswer?: ReflectionAnswer
): Promise<ApiResponse> => {
  try {
    // This is the backend endpoint that securely handles the Gemini API call.
    // In a real deployment, this would point to your live server.
    const API_ENDPOINT = '/api/chat'; 

    const response = await fetch(API_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        history,
        reflectionAnswer,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({})); 
      const errorMessage = errorData.error || `A server error occurred (status: ${response.status})`;
      throw new Error(errorMessage);
    }

    const data: ApiResponse = await response.json();
    return data;

  } catch (error) {
    console.error('Failed to communicate with the backend service:', error);
    // This error is logged for debugging. The UI will show a user-friendly message from the calling component.
    throw new Error('Could not get a response from the AI. The backend service may be unavailable.');
  }
};
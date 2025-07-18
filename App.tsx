
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useSpeechRecognition } from './hooks/useSpeechRecognition.ts';
import { useSpeechSynthesis } from './hooks/useSpeechSynthesis.ts';
import { postChatMessage } from './services/geminiService.ts';
import type { Message, Emotion, MessageType } from './types.ts';
import { SamanthaOrb } from './components/SamanthaOrb.tsx';
import { ChatBubble } from './components/ChatBubble.tsx';
import { LogoIcon } from './components/icons/LogoIcon.tsx';

const App: React.FC = () => {
  const [conversation, setConversation] = useState<Message[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [reflectionContext, setReflectionContext] = useState<{ question: string } | null>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  const { isListening, transcript, startListening, stopListening, hasRecognitionSupport } = useSpeechRecognition();
  const { isSpeaking, speak } = useSpeechSynthesis();

  const addMessage = useCallback((sender: 'user' | 'ai', text: string, emotion?: Emotion, type: MessageType = 'standard') => {
    setConversation(prev => [...prev, { id: crypto.randomUUID(), sender, text, emotion, type }]);
  }, []);

  useEffect(() => {
    const welcomeMessage = "Hello, I'm Samantha. How are you feeling today?";
    addMessage('ai', welcomeMessage, 'neutral');
    speak(welcomeMessage);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const processTranscript = async () => {
      if (transcript && !isProcessing) {
        stopListening();
        addMessage('user', transcript);
        setIsProcessing(true);
        
        try {
          // If we are in a reflection context, send the answer. Otherwise, send null.
          const reflectionAnswer = reflectionContext ? { question: reflectionContext.question } : undefined;
          
          const { response: aiResponseText, emotion, type } = await postChatMessage(transcript, conversation, reflectionAnswer);
          
          addMessage('ai', aiResponseText, emotion, type);
          speak(aiResponseText);

          // If the AI's response is a reflection question, set the context for the next turn.
          if (type === 'reflection') {
            setReflectionContext({ question: aiResponseText });
          } else {
            // Clear reflection context after a standard response cycle is complete.
            setReflectionContext(null);
          }

        } catch (error) {
          console.error("Error processing transcript:", error);
          const errorMessage = "I'm having some trouble connecting to my thoughts. Please try again.";
          addMessage('ai', errorMessage, 'neutral');
          speak(errorMessage);
          setReflectionContext(null); // Clear context on error
        } finally {
          setIsProcessing(false);
        }
      }
    };
    processTranscript();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [transcript]);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [conversation]);

  const handleOrbClick = () => {
    if (isListening) {
      stopListening();
    } else if (!isSpeaking && !isProcessing) {
      startListening();
    }
  };

  return (
    <div className="flex h-screen w-full flex-col bg-slate-900 text-slate-100 font-sans">
      <header className="flex items-center justify-center p-4 border-b border-slate-700/50 shadow-lg">
        <div className="flex items-center">
            <LogoIcon />
            <h1 className="text-2xl font-bold ml-3 bg-gradient-to-r from-cyan-400 to-fuchsia-500 text-transparent bg-clip-text">
            SamanthaAI
            </h1>
        </div>
      </header>
      
      <main ref={chatContainerRef} className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6">
        {conversation.map((message) => (
          <ChatBubble key={message.id} message={message} />
        ))}
      </main>

      <footer className="flex flex-col items-center justify-center p-4 border-t border-slate-700/50">
        <SamanthaOrb 
          isListening={isListening} 
          isProcessing={isProcessing} 
          isSpeaking={isSpeaking}
          onClick={handleOrbClick}
        />
        {!hasRecognitionSupport && (
          <p className="mt-4 text-sm text-yellow-400">Speech recognition is not supported in your browser.</p>
        )}
         <p className="mt-3 text-sm text-slate-400">
          {reflectionContext ? 'Answering a reflection...' : 'Click the orb to speak'}
        </p>
      </footer>
    </div>
  );
};

export default App;
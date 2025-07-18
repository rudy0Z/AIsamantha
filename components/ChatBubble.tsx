
import React from 'react';
import { Message } from '../types.ts';
import { LogoIcon } from './icons/LogoIcon.tsx';

interface ChatBubbleProps {
  message: Message;
}

const emotionStyles: { [key: string]: string } = {
    happy: 'border-yellow-400/50',
    sad: 'border-blue-400/50',
    angry: 'border-red-500/50',
    curious: 'border-purple-400/50',
    excited: 'border-orange-400/50',
    neutral: 'border-slate-600/50',
};

export const ChatBubble: React.FC<ChatBubbleProps> = ({ message }) => {
  const isUser = message.sender === 'user';
  
  const bubbleClasses = isUser
    ? 'bg-blue-600/80 rounded-br-none self-end'
    : `bg-slate-700/80 rounded-bl-none self-start border-l-4 ${emotionStyles[message.emotion || 'neutral']}`;
    
  const containerClasses = isUser ? 'justify-end' : 'justify-start';

  return (
    <div className={`flex items-end gap-2 w-full ${containerClasses}`}>
       {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center border border-slate-700">
           <LogoIcon className="w-5 h-5" />
        </div>
       )}
       <div
        className={`max-w-xs md:max-w-md lg:max-w-2xl px-4 py-3 rounded-2xl shadow-md text-slate-50 transition-all duration-300 ${bubbleClasses}`}
      >
        <p className="whitespace-pre-wrap">{message.text}</p>
      </div>
    </div>
  );
};
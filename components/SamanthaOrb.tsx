
import React from 'react';
import { MicIcon } from './icons/MicIcon.tsx';
import { LoadingIcon } from './icons/LoadingIcon.tsx';

interface SamanthaOrbProps {
  isListening: boolean;
  isProcessing: boolean;
  isSpeaking: boolean;
  onClick: () => void;
}

export const SamanthaOrb: React.FC<SamanthaOrbProps> = ({ isListening, isProcessing, isSpeaking, onClick }) => {
  const isDisabled = isSpeaking || isProcessing;

  const getOrbStateClasses = () => {
    if (isSpeaking) {
      return 'bg-fuchsia-500 shadow-fuchsia-500/60 animate-pulse';
    }
    if (isListening) {
      return 'bg-cyan-500 shadow-cyan-400/70 scale-110';
    }
    if (isProcessing) {
      return 'bg-slate-600';
    }
    return 'bg-slate-700 hover:bg-cyan-600/50 shadow-cyan-500/30';
  };

  return (
    <button
      onClick={onClick}
      disabled={isDisabled}
      className={`relative flex items-center justify-center w-20 h-20 rounded-full transition-all duration-300 ease-in-out shadow-2xl focus:outline-none focus:ring-4 focus:ring-cyan-500/50 ${getOrbStateClasses()} ${isDisabled ? 'cursor-not-allowed' : 'cursor-pointer'}`}
      aria-label={isListening ? 'Stop listening' : 'Start listening'}
    >
      <span className="absolute inset-0 rounded-full animate-ping opacity-25" style={{
          animationDuration: '2s',
          backgroundColor: isListening ? 'rgb(103 232 249)' : isSpeaking ? 'rgb(217 70 239)' : 'transparent',
      }}></span>

      {isProcessing ? (
        <LoadingIcon className="w-8 h-8 text-slate-300" />
      ) : (
        <MicIcon className="w-8 h-8 text-slate-200" />
      )}
    </button>
  );
};
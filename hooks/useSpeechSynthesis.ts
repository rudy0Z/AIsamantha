
import { useState, useEffect, useCallback, useRef } from 'react';

export const useSpeechSynthesis = () => {
    const [isSpeaking, setIsSpeaking] = useState(false);
    const synthRef = useRef<SpeechSynthesis | null>(null);

    useEffect(() => {
        if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
            synthRef.current = window.speechSynthesis;
        }

        const handleVoicesChanged = () => {
            // Voices are now loaded
        };

        if (synthRef.current) {
            synthRef.current.addEventListener('voiceschanged', handleVoicesChanged);
        }

        return () => {
            if (synthRef.current) {
                synthRef.current.removeEventListener('voiceschanged', handleVoicesChanged);
                synthRef.current.cancel();
            }
        };
    }, []);

    const speak = useCallback((text: string) => {
        if (!synthRef.current || isSpeaking) {
            return;
        }

        const utterance = new SpeechSynthesisUtterance(text);
        
        const voices = synthRef.current.getVoices();
        let selectedVoice = voices.find(voice => voice.name === 'Samantha' || voice.name === 'Google US English');
        if (!selectedVoice) {
            selectedVoice = voices.find(voice => voice.lang === 'en-US' && voice.name.includes('Female'));
        }
        if (!selectedVoice) {
            selectedVoice = voices.find(voice => voice.lang === 'en-US');
        }
        
        utterance.voice = selectedVoice || voices[0];
        utterance.pitch = 1.1;
        utterance.rate = 1;

        utterance.onstart = () => setIsSpeaking(true);
        utterance.onend = () => setIsSpeaking(false);
        utterance.onerror = (e) => {
            console.error('Speech synthesis error', e);
            setIsSpeaking(false);
        };

        synthRef.current.speak(utterance);
    }, [isSpeaking]);

    return { isSpeaking, speak, hasSynthesisSupport: !!synthRef.current };
};

import { useState, useEffect, useRef, useCallback } from 'react';

// Define necessary interfaces for the Web Speech API, which is not a standard part of TypeScript's DOM library.
// This prevents TypeScript errors for non-standard, vendor-prefixed browser APIs.

// Represents the event fired when speech is recognized.
interface SpeechRecognitionEvent extends Event {
    readonly resultIndex: number;
    readonly results: SpeechRecognitionResultList;
}

// Represents a list of recognition results.
interface SpeechRecognitionResultList {
    readonly length: number;
    item(index: number): SpeechRecognitionResult;
    [index: number]: SpeechRecognitionResult;
}

// Represents a single recognition result, which may be final or intermediate.
interface SpeechRecognitionResult {
    readonly isFinal: boolean;
    readonly length: number;
    item(index: number): SpeechRecognitionAlternative;
    [index: number]: SpeechRecognitionAlternative;
}

// Represents a single possible transcript for a recognition result.
interface SpeechRecognitionAlternative {
    readonly transcript: string;
    readonly confidence: number;
}

// Represents a recognition error.
interface SpeechRecognitionErrorEvent extends Event {
    readonly error: string;
    readonly message: string;
}

// Represents the Speech Recognition service instance.
interface SpeechRecognition extends EventTarget {
    continuous: boolean;
    lang: string;
    interimResults: boolean;
    maxAlternatives: number;
    onend: (() => void) | null;
    onerror: ((event: SpeechRecognitionErrorEvent) => void) | null;
    onresult: ((event: SpeechRecognitionEvent) => void) | null;
    start(): void;
    stop(): void;
    abort(): void;
}

// Represents the constructor for the SpeechRecognition object.
interface SpeechRecognitionStatic {
    new (): SpeechRecognition;
}

// Augment the global Window interface to include SpeechRecognition and its prefixed version.
declare global {
    interface Window {
        SpeechRecognition: SpeechRecognitionStatic;
        webkitSpeechRecognition: SpeechRecognitionStatic;
    }
}


// Polyfill for browsers that might not have it on `window`.
const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;

export const useSpeechRecognition = () => {
    const [isListening, setIsListening] = useState(false);
    const [transcript, setTranscript] = useState('');
    const recognitionRef = useRef<SpeechRecognition | null>(null);

    useEffect(() => {
        if (!SpeechRecognitionAPI) {
            // The UI will show a message, so a console error is not necessary and might be alarming.
            return;
        }

        const recognition = new SpeechRecognitionAPI();
        recognition.continuous = false; // Stop after a pause
        recognition.lang = 'en-US';
        recognition.interimResults = false;

        recognition.onresult = (event: SpeechRecognitionEvent) => {
            const lastResult = event.results[event.results.length - 1];
            if (lastResult.isFinal) {
                setTranscript(lastResult[0].transcript);
            }
        };

        recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
            console.error('Speech recognition error:', event.error);
            setIsListening(false);
        };

        recognition.onend = () => {
            setIsListening(false);
        };

        recognitionRef.current = recognition;

        return () => {
            if(recognitionRef.current) {
                recognitionRef.current.stop();
            }
        };
    }, []);

    const startListening = useCallback(() => {
        if (recognitionRef.current && !isListening) {
            setTranscript('');
            try {
                recognitionRef.current.start();
                setIsListening(true);
            } catch (error) {
                console.error("Could not start recognition:", error);
                setIsListening(false);
            }
        }
    }, [isListening]);

    const stopListening = useCallback(() => {
        if (recognitionRef.current && isListening) {
            recognitionRef.current.stop();
            setIsListening(false);
        }
    }, [isListening]);

    return {
        isListening,
        transcript,
        startListening,
        stopListening,
        hasRecognitionSupport: !!SpeechRecognitionAPI,
    };
};

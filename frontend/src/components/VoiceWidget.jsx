import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Volume2, Send, Radio, MessageSquare, Sparkles } from 'lucide-react';

export default function VoiceWidget({ onVoiceAgentExecuted }) {
  const [isOpen, setIsOpen] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [responses, setResponses] = useState([]);
  const [statusText, setStatusText] = useState('VOX-AI V4 Engine Ready');
  const wsRef = useRef(null);
  const recognitionRef = useRef(null);

  useEffect(() => {
    // Web Speech API Initialization
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        setIsListening(true);
        setStatusText('Listening to voice directive...');
      };

      recognition.onresult = (event) => {
        let currentTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          currentTranscript += event.results[i][0].transcript;
        }
        setTranscript(currentTranscript);
      };

      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        setStatusText('Voice input error. Try again.');
      };

      recognition.onend = () => {
        setIsListening(false);
        setStatusText('Processing voice directive...');
      };

      recognitionRef.current = recognition;
    } else {
      setStatusText('Web Speech API not supported on this browser');
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/voice`;

    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setStatusText('Connected to VOX-AI V4 WebSocket Core');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'voice_response') {
          setResponses((prev) => [data, ...prev]);
          setStatusText(`Executed via ${data.agent_executed}`);

          // Browser Text-to-Speech playback
          if ('speechSynthesis' in window && data.spoken_response) {
            const utterance = new SpeechSynthesisUtterance(data.spoken_response);
            utterance.rate = 1.05;
            utterance.pitch = 1.0;
            window.speechSynthesis.speak(utterance);
          }

          if (onVoiceAgentExecuted) {
            onVoiceAgentExecuted(data);
          }
        }
      } catch (e) {
        console.error('Error parsing WebSocket voice payload:', e);
      }
    };

    ws.onclose = () => {
      setStatusText('VOX-AI WebSocket Disconnected');
    };

    wsRef.current = ws;
  };

  const toggleVoiceModal = () => {
    setIsOpen(!isOpen);
    if (!isOpen) {
      connectWebSocket();
    }
  };

  const startListening = () => {
    if (recognitionRef.current) {
      setTranscript('');
      recognitionRef.current.start();
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  };

  const sendVoiceCommand = (cmdText) => {
    const textToSend = cmdText || transcript;
    if (!textToSend.trim()) return;

    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      connectWebSocket();
      setTimeout(() => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.send(JSON.stringify({ transcript: textToSend }));
        }
      }, 500);
    } else {
      wsRef.current.send(JSON.stringify({ transcript: textToSend }));
    }
    setTranscript('');
  };

  return (
    <>
      {/* Floating Trigger Button */}
      <button
        onClick={toggleVoiceModal}
        className="fixed bottom-6 right-6 z-40 p-4 rounded-2xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-bold shadow-2xl shadow-cyan-500/40 hover:scale-105 active:scale-95 transition-all flex items-center gap-3 border border-cyan-400/30 group"
      >
        <div className="p-2 bg-white/20 rounded-xl group-hover:bg-white/30 transition">
          <Radio className="w-6 h-6 animate-pulse text-cyan-200" />
        </div>
        <div className="text-left hidden sm:block">
          <div className="text-xs uppercase font-extrabold tracking-widest text-cyan-200">VOX-AI V4</div>
          <div className="text-sm font-bold">Talk to Company</div>
        </div>
      </button>

      {/* Voice Control Modal / Drawer */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
          <div className="w-full max-w-lg bg-slate-900 border border-cyan-500/30 rounded-3xl p-6 shadow-2xl relative overflow-hidden">
            {/* Background Glow */}
            <div className="absolute -top-24 -right-24 w-48 h-48 bg-cyan-500/20 rounded-full blur-3xl pointer-events-none" />

            {/* Header */}
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-cyan-500/20 text-cyan-400 border border-cyan-500/40">
                  <Volume2 className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    VOX-AI V4 Voice Core <Sparkles className="w-4 h-4 text-cyan-400" />
                  </h3>
                  <p className="text-xs text-slate-400 font-mono">{statusText}</p>
                </div>
              </div>
              <button
                onClick={toggleVoiceModal}
                className="text-slate-400 hover:text-white p-2 rounded-lg hover:bg-slate-800 transition"
              >
                ✕
              </button>
            </div>

            {/* Microphone Control Area */}
            <div className="my-8 flex flex-col items-center justify-center">
              <button
                onClick={isListening ? stopListening : startListening}
                className={`p-8 rounded-full border-4 transition-all duration-300 shadow-2xl ${
                  isListening
                    ? 'bg-red-500/20 border-red-500 text-red-400 animate-pulse ring-8 ring-red-500/20'
                    : 'bg-cyan-500/20 border-cyan-500 text-cyan-400 hover:bg-cyan-500/30 ring-8 ring-cyan-500/10'
                }`}
              >
                {isListening ? <MicOff className="w-12 h-12" /> : <Mic className="w-12 h-12" />}
              </button>
              <p className="mt-4 text-xs font-semibold uppercase tracking-wider text-slate-400">
                {isListening ? 'Tap to Stop Listening' : 'Tap Mic & Speak Directive'}
              </p>
            </div>

            {/* Live Transcript Display / Manual Prompt */}
            <div className="space-y-3">
              <div className="relative">
                <input
                  type="text"
                  value={transcript}
                  onChange={(e) => setTranscript(e.target.value)}
                  placeholder="e.g. Sales team, find 10 leads in Hamburg..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl py-3 pl-4 pr-12 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-sans"
                />
                <button
                  onClick={() => sendVoiceCommand()}
                  className="absolute right-2 top-2 p-1.5 bg-cyan-500 text-slate-950 rounded-lg hover:bg-cyan-400 transition"
                >
                  <Send className="w-4 h-4 font-bold" />
                </button>
              </div>

              {/* Sample Quick Directives */}
              <div className="flex flex-wrap gap-2 pt-2">
                <button
                  onClick={() => sendVoiceCommand('Sales team, find 10 leads in Hamburg')}
                  className="text-xs bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 px-3 py-1.5 rounded-lg text-slate-300 transition"
                >
                  "Find 10 leads in Hamburg"
                </button>
                <button
                  onClick={() => sendVoiceCommand('Run quantum QAOA task optimization')}
                  className="text-xs bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 px-3 py-1.5 rounded-lg text-slate-300 transition"
                >
                  "Quantum QAOA optimize"
                </button>
              </div>
            </div>

            {/* Response Log */}
            {responses.length > 0 && (
              <div className="mt-6 border-t border-slate-800 pt-4 max-h-48 overflow-y-auto space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                  <MessageSquare className="w-3.5 h-3.5 text-cyan-400" /> Executive Voice Logs
                </h4>
                {responses.map((res, idx) => (
                  <div key={idx} className="p-3 bg-slate-950/80 rounded-xl border border-slate-800 text-xs space-y-1">
                    <div className="flex justify-between text-cyan-400 font-semibold">
                      <span>Agent: {res.agent_executed}</span>
                      <span className="text-[10px] text-slate-500">{res.department || 'SYSTEM'}</span>
                    </div>
                    <p className="text-slate-300">{res.spoken_response}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}

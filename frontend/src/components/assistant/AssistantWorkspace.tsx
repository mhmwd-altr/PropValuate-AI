import React, { useState, useEffect, useRef } from 'react';
import {
  Send,
  Sparkles,
  RotateCcw,
  Building2,
  MapPin,
  CheckCircle2,
  AlertCircle,
  Clock,
  Layers,
  HelpCircle,
  ShieldCheck,
} from 'lucide-react';
import { assistantClient } from '../../api/assistantClient';
import {
  ChatMessage,
  PropertySlotsState,
  ValuationToolResult,
} from '../../types/assistant';

const INITIAL_GREETING: ChatMessage = {
  id: 'greeting-msg',
  role: 'assistant',
  content:
    'Hello! I am PropValuate AI Assistant. I can help you estimate property prices across 81 Indian cities, extract property details from natural language, or answer real estate questions.',
  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
  intent: 'GENERAL_REAL_ESTATE_QUESTION',
};

const SUGGESTED_PROMPTS = [
  'Estimate price for a 1500 sqft 3 BHK flat in Bangalore.',
  'What is the value of a 2 BHK apartment (1100 sqft) in Mumbai, resale?',
  'Which cities in India are supported for valuation?',
  'What is RERA and how does it protect buyers?',
];

export const AssistantWorkspace: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([INITIAL_GREETING]);
  const [inputText, setInputText] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [accumulatedSlots, setAccumulatedSlots] = useState<PropertySlotsState>({});
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSendMessage = async (textToSend?: string) => {
    const text = (textToSend || inputText).trim();
    if (!text || isLoading) return;

    setError(null);
    setInputText('');

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const response = await assistantClient.sendMessage(text, sessionId);
      
      if (!sessionId) {
        setSessionId(response.session_id);
      }

      setAccumulatedSlots(response.slots || {});

      const assistantMsg: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.reply,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        intent: response.intent,
        toolCalled: response.tool_called,
        toolResult: response.tool_result,
        slots: response.slots,
        missingSlots: response.missing_slots,
        isValuationComplete: response.is_valuation_complete,
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      setError(err.message || 'Unable to connect to AI Assistant. Please check backend connection.');
    } finally {
      setIsLoading(false);
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  const handleResetSession = async () => {
    if (sessionId) {
      try {
        await assistantClient.resetSession(sessionId);
      } catch (err) {
        console.warn('Session reset failed on backend:', err);
      }
    }
    setSessionId(null);
    setAccumulatedSlots({});
    setMessages([
      {
        id: `reset-${Date.now()}`,
        role: 'assistant',
        content:
          'Session cleared. You can start a new valuation by describing your property (e.g. area in sqft, BHK, and city).',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        intent: 'GENERAL_REAL_ESTATE_QUESTION',
      },
    ]);
    setError(null);
    inputRef.current?.focus();
  };

  const renderValuationCard = (result: ValuationToolResult) => {
    return (
      <div className="mt-4 p-5 rounded-2xl bg-gradient-to-br from-brand-900 to-slate-900 text-white shadow-lg border border-brand-700/40 animate-fade-in">
        <div className="flex items-center justify-between border-b border-brand-800/80 pb-3 mb-4">
          <div className="flex items-center space-x-2">
            <div className="p-1.5 rounded-lg bg-brand-600/30 text-brand-300">
              <Building2 className="w-5 h-5" />
            </div>
            <div>
              <span className="text-xs font-semibold uppercase tracking-wider text-brand-300">
                Authoritative Valuation
              </span>
              <p className="text-xs text-slate-400">Valuation Engine V2 (HistGradientBoosting)</p>
            </div>
          </div>
          <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" /> Verified
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <span className="text-xs text-slate-400">Estimated Market Valuation</span>
            <div className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-0.5">
              ₹ {result.predicted_price_lakhs.toLocaleString('en-IN')} <span className="text-base font-medium text-brand-200">Lakhs</span>
            </div>
            <div className="text-xs text-slate-400 mt-1">
              ₹ {result.predicted_price.toLocaleString('en-IN', { maximumFractionDigits: 0 })} INR
            </div>
          </div>

          <div className="bg-white/5 rounded-xl p-3 border border-white/10 flex flex-col justify-center">
            <div className="text-xs text-slate-300 flex justify-between">
              <span>Avg Rate:</span>
              <span className="font-semibold text-white">₹ {result.rate_per_sqft.toLocaleString('en-IN')}/sqft</span>
            </div>
            {result.engineered_features && (
              <div className="text-xs text-slate-300 flex justify-between mt-1">
                <span>Nearest Metro:</span>
                <span className="font-semibold text-white">{result.engineered_features.dist_nearest_metro_km} km</span>
              </div>
            )}
          </div>
        </div>

        {result.property_details && (
          <div className="mt-4 pt-3 border-t border-brand-800/80 flex flex-wrap gap-2 text-xs text-slate-300">
            <span className="px-2 py-0.5 rounded bg-white/10">{result.property_details.bhk} BHK</span>
            <span className="px-2 py-0.5 rounded bg-white/10">{result.property_details.area_sqft} sqft</span>
            <span className="px-2 py-0.5 rounded bg-white/10">{result.property_details.city}</span>
            <span className="px-2 py-0.5 rounded bg-white/10">{result.property_details.posted_by}</span>
            {result.property_details.rera && (
              <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300">RERA Approved</span>
            )}
          </div>
        )}
      </div>
    );
  };

  const hasActiveSlots =
    accumulatedSlots.area_sqft ||
    accumulatedSlots.bhk ||
    accumulatedSlots.city ||
    accumulatedSlots.rera !== undefined;

  return (
    <div className="w-full max-w-4xl mx-auto flex flex-col h-[750px] bg-white rounded-3xl shadow-xl border border-slate-200/80 overflow-hidden">
      {/* Workspace Header */}
      <div className="px-6 py-4 bg-slate-900 text-white flex items-center justify-between border-b border-slate-800">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center text-white shadow-md shadow-brand-500/20">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="font-bold text-base text-white tracking-tight">
                PropValuate Assistant
              </h2>
              <span className="px-2 py-0.5 rounded-full text-2xs font-semibold bg-brand-500/30 text-brand-300 border border-brand-400/30">
                Qwen 2.5 3B (GGUF)
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Natural Language Real Estate Intelligence for India
            </p>
          </div>
        </div>

        <button
          onClick={handleResetSession}
          title="Clear conversation and reset property slots"
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-xs font-medium transition-colors border border-slate-700"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>New Session</span>
        </button>
      </div>

      {/* Active Property Slot Tracker Banner */}
      {hasActiveSlots && (
        <div className="px-6 py-2.5 bg-brand-50/70 border-b border-brand-100 flex items-center justify-between flex-wrap gap-2 text-xs">
          <div className="flex items-center space-x-2 text-brand-900 font-medium">
            <Layers className="w-4 h-4 text-brand-600" />
            <span>Captured Details:</span>
          </div>
          <div className="flex items-center space-x-1.5 flex-wrap gap-1.5">
            {accumulatedSlots.city && (
              <span className="px-2 py-0.5 rounded-md bg-white border border-brand-200 text-brand-800 font-semibold flex items-center gap-1">
                <MapPin className="w-3 h-3 text-brand-500" /> {accumulatedSlots.city.toUpperCase()}
              </span>
            )}
            {accumulatedSlots.bhk && (
              <span className="px-2 py-0.5 rounded-md bg-white border border-brand-200 text-brand-800 font-semibold">
                {accumulatedSlots.bhk} BHK
              </span>
            )}
            {accumulatedSlots.area_sqft && (
              <span className="px-2 py-0.5 rounded-md bg-white border border-brand-200 text-brand-800 font-semibold">
                {accumulatedSlots.area_sqft} sqft
              </span>
            )}
            {accumulatedSlots.rera === 1 && (
              <span className="px-2 py-0.5 rounded-md bg-emerald-100 border border-emerald-300 text-emerald-800 font-semibold flex items-center gap-0.5">
                <ShieldCheck className="w-3 h-3" /> RERA
              </span>
            )}
          </div>
        </div>
      )}

      {/* Message Timeline */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-slate-50/50">
        {messages.map((msg) => {
          const isUser = msg.role === 'user';
          const isValuationTool = msg.toolCalled === 'predict_property_price' && msg.toolResult;

          return (
            <div
              key={msg.id}
              className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}
            >
              <div
                className={`max-w-[85%] sm:max-w-[75%] rounded-2xl px-4 py-3.5 shadow-2xs ${
                  isUser
                    ? 'bg-brand-600 text-white rounded-br-xs'
                    : 'bg-white text-slate-800 border border-slate-200/90 rounded-bl-xs'
                }`}
              >
                <div className="text-sm leading-relaxed whitespace-pre-wrap font-normal">
                  {msg.content}
                </div>

                {/* Render Valuation Result Card if tool succeeded */}
                {!isUser && isValuationTool && renderValuationCard(msg.toolResult)}

                {/* Render missing slots chips if asking for clarification */}
                {!isUser && msg.missingSlots && msg.missingSlots.length > 0 && (
                  <div className="mt-3 pt-2.5 border-t border-slate-100 flex flex-wrap gap-1.5 items-center">
                    <span className="text-xs text-amber-700 font-medium flex items-center gap-1">
                      <HelpCircle className="w-3.5 h-3.5" /> Needed:
                    </span>
                    {msg.missingSlots.map((slot) => (
                      <span
                        key={slot}
                        className="px-2 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200 text-xs font-semibold"
                      >
                        {slot.replace('_', ' ').toUpperCase()}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              <span className="text-2xs text-slate-400 mt-1 px-1 flex items-center space-x-1">
                <Clock className="w-2.5 h-2.5" />
                <span>{msg.timestamp}</span>
              </span>
            </div>
          );
        })}

        {isLoading && (
          <div className="flex items-center space-x-2 text-slate-500 text-xs p-3 bg-white rounded-2xl border border-slate-200/80 w-fit animate-pulse">
            <Sparkles className="w-4 h-4 text-brand-600 animate-spin" />
            <span>Analyzing real estate request and calculating valuation...</span>
          </div>
        )}

        {error && (
          <div className="p-3 bg-red-50 text-red-700 rounded-2xl border border-red-200 text-xs flex items-start space-x-2">
            <AlertCircle className="w-4 h-4 mt-0.5 text-red-500 shrink-0" />
            <div>
              <p className="font-semibold">Request Error</p>
              <p>{error}</p>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Quick Suggestion Pills */}
      <div className="px-6 py-2 bg-slate-100/70 border-t border-slate-200/60 overflow-x-auto flex space-x-2 scrollbar-none">
        {SUGGESTED_PROMPTS.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => handleSendMessage(prompt)}
            disabled={isLoading}
            className="shrink-0 text-xs px-3 py-1.5 rounded-full bg-white hover:bg-brand-50 hover:text-brand-700 text-slate-600 border border-slate-200/80 transition-all active:scale-98 disabled:opacity-50"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input Form Bar */}
      <div className="p-4 bg-white border-t border-slate-200">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          className="flex items-center space-x-2"
        >
          <input
            ref={inputRef}
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Type your property question or details (e.g. 1500 sqft 3 BHK in Bangalore)..."
            disabled={isLoading}
            maxLength={1000}
            className="flex-1 px-4 py-3 bg-slate-50 border border-slate-200 rounded-2xl text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:bg-white transition-all placeholder:text-slate-400"
          />

          <button
            type="submit"
            disabled={!inputText.trim() || isLoading}
            className="px-5 py-3 rounded-2xl bg-brand-600 hover:bg-brand-700 disabled:bg-slate-200 text-white font-semibold text-sm flex items-center space-x-2 shadow-sm shadow-brand-600/20 transition-all active:scale-98 cursor-pointer disabled:cursor-not-allowed"
          >
            <span>Send</span>
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};

import React from 'react';
import { AssistantWorkspace } from '../components/assistant/AssistantWorkspace';
import { Sparkles, Shield, MapPin, Cpu } from 'lucide-react';

export const AssistantPage: React.FC = () => {
  return (
    <div className="space-y-8">
      {/* Page Hero Header */}
      <div className="text-center max-w-2xl mx-auto space-y-3">
        <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-brand-50 border border-brand-200/80 text-brand-700 text-xs font-semibold shadow-2xs">
          <Sparkles className="w-3.5 h-3.5 text-brand-600" />
          <span>Conversational Real Estate AI</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
          AI Property Valuation Assistant
        </h1>
        <p className="text-sm sm:text-base text-slate-600">
          Describe any residential property in natural language or Hinglish. Our local Language AI extracts key parameters and runs verified Valuation Engine V2 machine-learning predictions.
        </p>
      </div>

      {/* Main Interactive Assistant Workspace */}
      <AssistantWorkspace />

      {/* Feature Capability Badges */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-4xl mx-auto text-xs text-slate-600 pt-4">
        <div className="p-4 rounded-2xl bg-white border border-slate-200/80 shadow-2xs flex items-start space-x-3">
          <div className="p-2 rounded-xl bg-brand-50 text-brand-600 shrink-0">
            <Cpu className="w-4 h-4" />
          </div>
          <div>
            <h4 className="font-bold text-slate-900">Local Small Language Model</h4>
            <p className="text-slate-500 mt-0.5">Powered by Qwen 2.5 3B Instruct running locally with GGUF quantization.</p>
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-slate-200/80 shadow-2xs flex items-start space-x-3">
          <div className="p-2 rounded-xl bg-emerald-50 text-emerald-600 shrink-0">
            <Shield className="w-4 h-4" />
          </div>
          <div>
            <h4 className="font-bold text-slate-900">Zero Numeric Hallucination</h4>
            <p className="text-slate-500 mt-0.5">All valuations are computed by deterministic ML pipelines, never guessed by the LLM.</p>
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-slate-200/80 shadow-2xs flex items-start space-x-3">
          <div className="p-2 rounded-xl bg-indigo-50 text-indigo-600 shrink-0">
            <MapPin className="w-4 h-4" />
          </div>
          <div>
            <h4 className="font-bold text-slate-900">81 Indian Cities Registry</h4>
            <p className="text-slate-500 mt-0.5">Automated spatial distance and coordinate resolution for all verified Indian metros.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

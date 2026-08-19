import React from 'react';
import { Building2, ShieldCheck, Database, Cpu } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-white border-t border-slate-200 mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8 pb-8 border-b border-slate-100">
          <div>
            <div className="flex items-center space-x-2 mb-3">
              <div className="w-7 h-7 rounded-lg bg-brand-600 flex items-center justify-center text-white">
                <Building2 className="w-4 h-4" />
              </div>
              <span className="font-bold text-slate-900">PropValuate AI</span>
            </div>
            <p className="text-sm text-slate-500 leading-relaxed">
              Production machine-learning system for estimating real-estate valuations across 81 Indian cities based on verified spatial and architectural attributes.
            </p>
          </div>

          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900 mb-3 flex items-center space-x-1.5">
              <Cpu className="w-4 h-4 text-brand-600" />
              <span>Technology Architecture</span>
            </h4>
            <ul className="text-xs text-slate-600 space-y-2 font-medium">
              <li className="flex items-center space-x-2">
                <span className="w-1.5 h-1.5 rounded-full bg-brand-500"></span>
                <span>Scikit-Learn Regression Pipeline</span>
              </li>
              <li className="flex items-center space-x-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                <span>FastAPI Asynchronous Backend</span>
              </li>
              <li className="flex items-center space-x-2">
                <span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
                <span>React + TypeScript + Vite Interface</span>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900 mb-3 flex items-center space-x-1.5">
              <ShieldCheck className="w-4 h-4 text-brand-600" />
              <span>Model & Methodology Note</span>
            </h4>
            <p className="text-xs text-slate-500 leading-relaxed">
              Estimates are generated algorithmically using trained HistGradientBoosting models with 5-fold cross-validation. Valuations are informative estimates based on historical market data.
            </p>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 space-y-2 sm:space-y-0">
          <p>© {new Date().getFullYear()} PropValuate AI. All rights reserved.</p>
          <div className="flex items-center space-x-4">
            <span className="flex items-center space-x-1">
              <Database className="w-3.5 h-3.5 text-slate-400" />
              <span>81 Cities Supported</span>
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
};

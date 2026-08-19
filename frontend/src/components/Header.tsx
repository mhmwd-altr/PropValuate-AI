import React from 'react';
import { Link } from 'react-router-dom';
import { Building2, Sparkles } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="sticky top-0 z-30 bg-white/90 backdrop-blur-md border-b border-slate-200/80 shadow-2xs transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link
          to="/"
          className="flex items-center space-x-3 group transition-opacity hover:opacity-95"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-700 to-brand-500 flex items-center justify-center text-white shadow-sm shadow-brand-500/20 group-hover:scale-105 transition-transform">
            <Building2 className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg text-slate-900 tracking-tight">
                PropValuate
              </span>
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-brand-50 text-brand-700 border border-brand-200/60">
                <Sparkles className="w-3 h-3 mr-1 text-brand-600" /> AI
              </span>
            </div>
            <p className="text-xs text-slate-500 font-medium hidden sm:block">
              Residential Property Price Estimation
            </p>
          </div>
        </Link>

        <div className="flex items-center space-x-3 sm:space-x-4">
          <div className="hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-full bg-emerald-50 text-xs text-emerald-700 font-medium border border-emerald-200/60">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>Valuation Engine Online</span>
          </div>
          <Link
            to="/"
            className="text-xs sm:text-sm font-semibold text-slate-700 hover:text-brand-600 transition-colors px-3.5 py-2 rounded-xl hover:bg-slate-100/80 active:scale-98"
          >
            Valuation Tool
          </Link>
        </div>
      </div>
    </header>
  );
};

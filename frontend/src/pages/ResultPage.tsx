import React, { useState } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import {
  Sparkles,
  ArrowLeft,
  RotateCcw,
  MapPin,
  Maximize2,
  BedDouble,
  Bath,
  Layers,
  Building,
  KeyRound,
  FileText,
  Compass,
  CheckCircle2,
  ShieldCheck,
  TrendingUp,
  Copy,
  Check,
} from 'lucide-react';
import { ValuationResultState } from '../types/prediction';
import {
  formatINR,
  formatIndianDenomination,
  formatLocation,
  formatFloor,
} from '../utils/formatters';
import { useAnimatedNumber } from '../utils/useAnimatedNumber';

export const ResultPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [copied, setCopied] = useState<boolean>(false);

  const state = location.state as ValuationResultState | undefined;

  // Real ML predicted value
  const finalPrice = state?.result?.predicted_price || 0;
  const { animatedValue } = useAnimatedNumber(finalPrice, 850);

  // If page accessed directly without prediction state, render graceful fallback
  if (!state || !state.result || !state.inputs) {
    return (
      <div className="max-w-xl mx-auto text-center py-16 px-4 animate-fade-in-up">
        <div className="w-16 h-16 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center mx-auto mb-4 border border-amber-200 shadow-2xs">
          <Sparkles className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">
          No Valuation Available
        </h2>
        <p className="text-sm text-slate-600 mb-6 leading-relaxed">
          Please provide property specifications on the valuation tool to generate a real-time price estimation.
        </p>
        <Link
          to="/"
          className="inline-flex items-center space-x-2 px-6 py-3 rounded-xl bg-brand-600 text-white text-sm font-bold shadow-md hover:bg-brand-700 active:scale-[0.98] transition-all"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Go to Valuation Tool</span>
        </Link>
      </div>
    );
  }

  const { inputs, result, timestamp } = state;
  const denomination = formatIndianDenomination(result.predicted_price);
  const pricePerSqft =
    inputs.area_sqft > 0
      ? Math.round(result.predicted_price / inputs.area_sqft)
      : 0;

  const handleEditDetails = () => {
    navigate('/', { state: { editValues: inputs } });
  };

  const handlePredictNew = () => {
    navigate('/');
  };

  const handleCopySummary = async () => {
    try {
      const summaryText = `PropValuate AI Valuation Summary
Location: ${formatLocation(inputs.location)}
Carpet Area: ${inputs.area_sqft.toLocaleString('en-IN')} sq ft (${inputs.bhk} BHK)
Estimated Valuation: ${formatINR(result.predicted_price)} (${denomination.compact})
Rate: ₹${pricePerSqft.toLocaleString('en-IN')} / sq ft
Generated: ${new Date(timestamp).toLocaleDateString('en-IN')}`;
      await navigator.clipboard.writeText(summaryText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch {
      // Clipboard fallback
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 sm:space-y-8 animate-fade-in-up">
      {/* Top Back Navigation & Action Bar */}
      <div className="flex items-center justify-between">
        <button
          onClick={handleEditDetails}
          className="inline-flex items-center space-x-2 text-xs sm:text-sm font-bold text-slate-600 hover:text-brand-600 active:scale-[0.98] transition-all cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Edit Specifications</span>
        </button>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleCopySummary}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 active:scale-[0.98] shadow-2xs transition-all cursor-pointer"
            title="Copy property valuation summary to clipboard"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-600" />
                <span className="text-emerald-700">Copied</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5 text-slate-500" />
                <span>Copy Summary</span>
              </>
            )}
          </button>

          <div className="text-xs text-slate-400 font-medium hidden sm:block">
            Estimated on {new Date(timestamp).toLocaleDateString('en-IN', {
              day: 'numeric',
              month: 'short',
              year: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
            })}
          </div>
        </div>
      </div>

      {/* HERO VALUATION CARD (Staged Reveal 1 & 2) */}
      <div className="stagger-1 bg-gradient-to-br from-slate-900 via-slate-800 to-brand-950 rounded-3xl p-6 sm:p-10 lg:p-12 text-white shadow-hero relative overflow-hidden transition-all">
        {/* Subtle background ambient blur */}
        <div className="absolute -right-16 -bottom-16 w-64 h-64 rounded-full bg-brand-500/15 blur-3xl pointer-events-none"></div>

        <div className="relative z-10 flex flex-col md:flex-row md:items-end md:justify-between gap-6">
          <div>
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-400/30 text-emerald-300 text-xs font-semibold uppercase tracking-wider mb-4">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>Machine Learning Valuation</span>
            </div>

            <h2 className="text-xs sm:text-sm font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
              Estimated Property Value
            </h2>

            {/* Dominant Animated Price Display */}
            <div className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight text-white mb-3 tabular-nums">
              {formatINR(animatedValue)}
            </div>

            {/* Indian Denomination & Metric Badges */}
            <div className="flex flex-wrap items-center gap-2.5 pt-1">
              <span className="inline-flex items-center px-3.5 py-1 rounded-lg text-sm font-extrabold bg-brand-500/20 text-brand-200 border border-brand-400/30 shadow-2xs">
                {denomination.compact}
              </span>
              <span className="inline-flex items-center px-3 py-1 rounded-lg text-xs font-semibold bg-slate-800/90 text-slate-300 border border-slate-700 shadow-2xs">
                <TrendingUp className="w-3.5 h-3.5 mr-1 text-slate-400" />
                ₹{pricePerSqft.toLocaleString('en-IN')} / sq ft
              </span>
              <span className="inline-flex items-center px-3 py-1 rounded-lg text-xs font-semibold bg-slate-800/90 text-slate-300 border border-slate-700 shadow-2xs">
                <MapPin className="w-3.5 h-3.5 mr-1 text-brand-400" />
                {formatLocation(inputs.location)}
              </span>
            </div>
          </div>

          {/* Action CTAs inside Hero */}
          <div className="flex flex-col sm:flex-row md:flex-col gap-3 pt-2 md:pt-0 shrink-0">
            <button
              onClick={handlePredictNew}
              className="px-6 py-3.5 rounded-xl bg-white text-slate-900 text-sm font-bold shadow-md hover:bg-slate-100 hover:shadow-lg transition-all active:scale-[0.98] flex items-center justify-center space-x-2 cursor-pointer"
            >
              <RotateCcw className="w-4 h-4 text-brand-600" />
              <span>Valuate Another Property</span>
            </button>
            <button
              onClick={handleEditDetails}
              className="px-6 py-3.5 rounded-xl bg-slate-800/80 hover:bg-slate-800 text-slate-200 text-sm font-bold border border-slate-700 transition-all active:scale-[0.98] flex items-center justify-center space-x-2 cursor-pointer"
            >
              <span>Edit Specifications</span>
            </button>
          </div>
        </div>
      </div>

      {/* PROPERTY SPECIFICATIONS SUMMARY (Staged Reveal 3) */}
      <div className="stagger-2 bg-white rounded-2xl p-6 sm:p-8 border border-slate-200/80 shadow-soft">
        <div className="flex items-center justify-between pb-4 mb-6 border-b border-slate-100">
          <div>
            <h3 className="text-base font-bold text-slate-900">
              Submitted Property Specifications
            </h3>
            <p className="text-xs text-slate-500">
              Parameters provided for this valuation estimate
            </p>
          </div>
          <button
            onClick={handleEditDetails}
            className="text-xs font-bold text-brand-600 hover:text-brand-700 active:scale-[0.98] transition-all cursor-pointer"
          >
            Edit Parameters
          </button>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5 sm:gap-4">
          <div className="p-3.5 rounded-xl bg-slate-50/90 border border-slate-100 hover:border-slate-200 transition-all">
            <div className="text-slate-400 text-xs font-semibold uppercase flex items-center space-x-1.5 mb-1 select-none">
              <MapPin className="w-3.5 h-3.5 text-brand-500" />
              <span>Location</span>
            </div>
            <p className="text-sm font-bold text-slate-900 truncate">
              {formatLocation(inputs.location)}
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50/90 border border-slate-100 hover:border-slate-200 transition-all">
            <div className="text-slate-400 text-xs font-semibold uppercase flex items-center space-x-1.5 mb-1 select-none">
              <Maximize2 className="w-3.5 h-3.5 text-brand-500" />
              <span>Carpet Area</span>
            </div>
            <p className="text-sm font-bold text-slate-900">
              {inputs.area_sqft.toLocaleString('en-IN')} sq ft
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50/90 border border-slate-100 hover:border-slate-200 transition-all">
            <div className="text-slate-400 text-xs font-semibold uppercase flex items-center space-x-1.5 mb-1 select-none">
              <BedDouble className="w-3.5 h-3.5 text-brand-500" />
              <span>Bedrooms</span>
            </div>
            <p className="text-sm font-bold text-slate-900">
              {inputs.bhk} BHK
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50/90 border border-slate-100 hover:border-slate-200 transition-all">
            <div className="text-slate-400 text-xs font-semibold uppercase flex items-center space-x-1.5 mb-1 select-none">
              <Bath className="w-3.5 h-3.5 text-brand-500" />
              <span>Bathrooms</span>
            </div>
            <p className="text-sm font-bold text-slate-900">
              {inputs.bathroom}
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50/90 border border-slate-100 hover:border-slate-200 transition-all">
            <div className="text-slate-400 text-xs font-semibold uppercase flex items-center space-x-1.5 mb-1 select-none">
              <Layers className="w-3.5 h-3.5 text-brand-500" />
              <span>Balconies</span>
            </div>
            <p className="text-sm font-bold text-slate-900">
              {inputs.balcony}
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50/90 border border-slate-100 hover:border-slate-200 transition-all">
            <div className="text-slate-400 text-xs font-semibold uppercase flex items-center space-x-1.5 mb-1 select-none">
              <Building className="w-3.5 h-3.5 text-brand-500" />
              <span>Floor Level</span>
            </div>
            <p className="text-sm font-bold text-slate-900 truncate">
              {formatFloor(inputs.floor_num, inputs.total_floors)}
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50/90 border border-slate-100 hover:border-slate-200 transition-all">
            <div className="text-slate-400 text-xs font-semibold uppercase flex items-center space-x-1.5 mb-1 select-none">
              <KeyRound className="w-3.5 h-3.5 text-brand-500" />
              <span>Furnishing</span>
            </div>
            <p className="text-sm font-bold text-slate-900 truncate">
              {inputs.Furnishing}
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50/90 border border-slate-100 hover:border-slate-200 transition-all">
            <div className="text-slate-400 text-xs font-semibold uppercase flex items-center space-x-1.5 mb-1 select-none">
              <FileText className="w-3.5 h-3.5 text-brand-500" />
              <span>Transaction</span>
            </div>
            <p className="text-sm font-bold text-slate-900 truncate">
              {inputs.Transaction}
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50/90 border border-slate-100 hover:border-slate-200 transition-all">
            <div className="text-slate-400 text-xs font-semibold uppercase flex items-center space-x-1.5 mb-1 select-none">
              <Compass className="w-3.5 h-3.5 text-brand-500" />
              <span>Facing</span>
            </div>
            <p className="text-sm font-bold text-slate-900 truncate">
              {inputs.facing}
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50/90 border border-slate-100 hover:border-slate-200 transition-all">
            <div className="text-slate-400 text-xs font-semibold uppercase flex items-center space-x-1.5 mb-1 select-none">
              <CheckCircle2 className="w-3.5 h-3.5 text-brand-500" />
              <span>Ownership</span>
            </div>
            <p className="text-sm font-bold text-slate-900 truncate">
              {inputs.Ownership}
            </p>
          </div>
        </div>
      </div>

      {/* Model Transparency & Methodology Card (Staged Reveal 4) */}
      <div className="stagger-3 bg-slate-100/80 rounded-2xl p-5 border border-slate-200/80 flex items-start space-x-3.5">
        <ShieldCheck className="w-5 h-5 text-slate-500 shrink-0 mt-0.5" />
        <div className="text-xs text-slate-600 leading-relaxed">
          <span className="font-bold text-slate-800">
            Methodology & Confidence Disclosure:
          </span>{' '}
          This price estimation is generated algorithmically based on statistical patterns learned from historical residential property transactions. Actual market prices may vary based on exact locality micro-factors, property age, amenity quality, and negotiated terms.
        </div>
      </div>
    </div>
  );
};

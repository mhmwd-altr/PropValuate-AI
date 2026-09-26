import React from 'react';
import { useLocation } from 'react-router-dom';
import { PredictionForm } from '../components/PredictionForm';
import { Sparkles, MapPin, Zap, ShieldCheck } from 'lucide-react';
import { PredictionRequest, PredictionRequestV2 } from '../types/prediction';

export const HomePage: React.FC = () => {
  const location = useLocation();
  // If navigated back with existing form inputs, prefill them
  const initialValues = (location.state as { editValues?: PredictionRequest })?.editValues;
  const initialV2Values = (location.state as { editValuesV2?: PredictionRequestV2 })?.editValuesV2;
  const defaultMode = initialV2Values ? 'v2' : initialValues ? 'v1' : 'v2';


  return (
    <div className="space-y-10 sm:space-y-12 animate-fade-in-up">
      {/* Hero Section */}
      <section className="text-center max-w-3xl mx-auto pt-4 sm:pt-8">
        <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-brand-50 border border-brand-200/80 text-brand-700 text-xs font-bold uppercase tracking-wider mb-5 shadow-2xs">
          <Sparkles className="w-3.5 h-3.5 text-brand-600" />
          <span>AI-Powered Real Estate Valuation</span>
        </div>

        <h1 className="text-3xl sm:text-5xl font-extrabold text-slate-900 tracking-tight leading-tight sm:leading-tight mb-4">
          Estimate Residential Property Value with Precision
        </h1>

        <p className="text-base sm:text-lg text-slate-600 font-normal leading-relaxed">
          Trained on verified residential transactions across 81 major Indian metropolitan markets. Enter physical specifications, floor height, and locality to compute estimated valuation.
        </p>
      </section>

      {/* Main Interactive Form Card */}
      <div className="max-w-4xl mx-auto">
        <PredictionForm initialValues={initialValues} initialV2Values={initialV2Values} defaultMode={defaultMode as 'v1' | 'v2'} />
      </div>

      {/* Feature / Trust Badges */}
      <section className="max-w-5xl mx-auto pt-8 border-t border-slate-200/60">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-soft flex items-start space-x-3.5 transition-all hover:shadow-card hover:-translate-y-0.5">
            <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
              <MapPin className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-slate-900">81 Regional Markets</h4>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                Trained across major metropolitan hubs and tier-2 urban growth corridors nationwide.
              </p>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-soft flex items-start space-x-3.5 transition-all hover:shadow-card hover:-translate-y-0.5">
            <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
              <Zap className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-slate-900">Instant Valuation</h4>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                Real-time pricing estimates generated immediately from your property specifications.
              </p>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-soft flex items-start space-x-3.5 transition-all hover:shadow-card hover:-translate-y-0.5">
            <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-slate-900">Data-Driven Model</h4>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                Trained on verified residential transactions using validated machine learning algorithms.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

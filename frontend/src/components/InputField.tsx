import React from 'react';
import { AlertCircle } from 'lucide-react';

interface InputFieldProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  icon?: React.ReactNode;
  unit?: string;
  error?: string;
  helperText?: string;
}

export const InputField: React.FC<InputFieldProps> = ({
  label,
  icon,
  unit,
  error,
  helperText,
  className = '',
  id,
  ...props
}) => {
  const inputId = id || label.toLowerCase().replace(/[^a-z0-9]/g, '-');
  const errorId = `${inputId}-error`;
  const helperId = `${inputId}-helper`;

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-1.5">
        <label
          htmlFor={inputId}
          className="block text-xs font-semibold uppercase tracking-wider text-slate-700 select-none"
        >
          {label}
          {props.required && <span className="text-rose-500 ml-1" aria-hidden="true">*</span>}
        </label>
        {unit && (
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider select-none">
            {unit}
          </span>
        )}
      </div>

      <div className="relative rounded-xl shadow-xs transition-all">
        {icon && (
          <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
            {icon}
          </div>
        )}
        <input
          id={inputId}
          aria-invalid={Boolean(error)}
          aria-describedby={error ? errorId : helperText ? helperId : undefined}
          className={`
            w-full rounded-xl border bg-white py-2.5 text-sm font-medium text-slate-900 placeholder-slate-400
            transition-all duration-200 ease-out focus:outline-hidden
            ${icon ? 'pl-10' : 'pl-3.5'}
            ${unit ? 'pr-12' : 'pr-3.5'}
            ${
              error
                ? 'border-rose-300 bg-rose-50/30 text-rose-900 focus:border-rose-500 focus:ring-3 focus:ring-rose-500/15'
                : 'border-slate-200 hover:border-slate-300 focus:border-brand-500 focus:ring-3 focus:ring-brand-500/15'
            }
            ${className}
          `}
          {...props}
        />
        {unit && (
          <div className="absolute inset-y-0 right-0 pr-3.5 flex items-center pointer-events-none text-xs font-medium text-slate-400 select-none">
            {unit}
          </div>
        )}
      </div>

      {error ? (
        <p
          id={errorId}
          role="alert"
          className="mt-1.5 text-xs text-rose-600 font-medium flex items-center space-x-1 animate-fade-in-up"
        >
          <AlertCircle className="w-3.5 h-3.5 shrink-0" />
          <span>{error}</span>
        </p>
      ) : helperText ? (
        <p id={helperId} className="mt-1 text-xs text-slate-400">
          {helperText}
        </p>
      ) : null}
    </div>
  );
};

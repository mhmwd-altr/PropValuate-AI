import React from 'react';
import { AlertCircle } from 'lucide-react';

export interface SelectOption {
  value: string;
  label: string;
}

interface SelectFieldProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label: string;
  options: SelectOption[];
  icon?: React.ReactNode;
  error?: string;
  helperText?: string;
}

export const SelectField: React.FC<SelectFieldProps> = ({
  label,
  options,
  icon,
  error,
  helperText,
  className = '',
  id,
  ...props
}) => {
  const selectId = id || label.toLowerCase().replace(/[^a-z0-9]/g, '-');
  const errorId = `${selectId}-error`;
  const helperId = `${selectId}-helper`;

  return (
    <div className="w-full">
      <label
        htmlFor={selectId}
        className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1.5 select-none"
      >
        {label}
        {props.required && <span className="text-rose-500 ml-1" aria-hidden="true">*</span>}
      </label>

      <div className="relative rounded-xl shadow-xs transition-all">
        {icon && (
          <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
            {icon}
          </div>
        )}
        <select
          id={selectId}
          aria-invalid={Boolean(error)}
          aria-describedby={error ? errorId : helperText ? helperId : undefined}
          className={`
            w-full appearance-none rounded-xl border bg-white py-2.5 text-sm font-medium text-slate-900
            transition-all duration-200 ease-out focus:outline-hidden cursor-pointer
            ${icon ? 'pl-10' : 'pl-3.5'}
            pr-10
            ${
              error
                ? 'border-rose-300 bg-rose-50/30 text-rose-900 focus:border-rose-500 focus:ring-3 focus:ring-rose-500/15'
                : 'border-slate-200 hover:border-slate-300 focus:border-brand-500 focus:ring-3 focus:ring-brand-500/15'
            }
            ${className}
          `}
          {...props}
        >
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>

        <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3.5 text-slate-400">
          <svg className="w-4 h-4 fill-current" viewBox="0 0 20 20">
            <path
              d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
              clipRule="evenodd"
              fillRule="evenodd"
            />
          </svg>
        </div>
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

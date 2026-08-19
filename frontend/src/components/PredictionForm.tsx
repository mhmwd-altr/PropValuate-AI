import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  MapPin,
  Maximize2,
  BedDouble,
  Bath,
  Layers,
  Sparkles,
  Compass,
  KeyRound,
  FileText,
  Building,
  AlertTriangle,
  Loader2,
  CheckCircle2,
} from 'lucide-react';
import { PredictionRequest, FormValidationErrors } from '../types/prediction';
import { predictionClient } from '../api/predictionClient';
import { formatLocation } from '../utils/formatters';
import { InputField } from './InputField';
import { SelectField, SelectOption } from './SelectField';

interface PredictionFormProps {
  initialValues?: PredictionRequest;
}

const DEFAULT_FORM_VALUES: PredictionRequest = {
  area_sqft: 1200,
  bhk: 2,
  bathroom: 2,
  balcony: 1,
  floor_num: 3,
  total_floors: 10,
  location: 'bangalore',
  Furnishing: 'Semi-Furnished',
  Transaction: 'Resale',
  facing: 'East',
  Ownership: 'Freehold',
};

const FURNISHING_OPTIONS: SelectOption[] = [
  { value: 'Semi-Furnished', label: 'Semi-Furnished' },
  { value: 'Furnished', label: 'Furnished' },
  { value: 'Unfurnished', label: 'Unfurnished' },
];

const TRANSACTION_OPTIONS: SelectOption[] = [
  { value: 'Resale', label: 'Resale' },
  { value: 'New Property', label: 'New Property' },
  { value: 'Other', label: 'Other' },
  { value: 'Rent/Lease', label: 'Rent / Lease' },
];

const FACING_OPTIONS: SelectOption[] = [
  { value: 'East', label: 'East' },
  { value: 'North - East', label: 'North - East' },
  { value: 'North', label: 'North' },
  { value: 'West', label: 'West' },
  { value: 'South', label: 'South' },
  { value: 'North - West', label: 'North - West' },
  { value: 'South - East', label: 'South - East' },
  { value: 'South -West', label: 'South - West' },
];

const OWNERSHIP_OPTIONS: SelectOption[] = [
  { value: 'Freehold', label: 'Freehold' },
  { value: 'Leasehold', label: 'Leasehold' },
  { value: 'Co-operative Society', label: 'Co-operative Society' },
  { value: 'Power Of Attorney', label: 'Power Of Attorney' },
];

export const PredictionForm: React.FC<PredictionFormProps> = ({
  initialValues,
}) => {
  const navigate = useNavigate();

  const [formData, setFormData] = useState<PredictionRequest>(
    initialValues || DEFAULT_FORM_VALUES
  );
  const [locations, setLocations] = useState<string[]>([]);
  const [loadingLocations, setLoadingLocations] = useState<boolean>(true);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [errors, setErrors] = useState<FormValidationErrors>({});
  const [apiError, setApiError] = useState<string | null>(null);

  // Load verified locations on mount
  useEffect(() => {
    let isMounted = true;
    async function loadLocations() {
      try {
        setLoadingLocations(true);
        const locs = await predictionClient.getLocations();
        if (isMounted) {
          const sorted = [...locs].sort((a, b) => a.localeCompare(b));
          setLocations(sorted);
          if (sorted.length > 0 && !initialValues) {
            setFormData((prev) => ({
              ...prev,
              location: prev.location || sorted[0],
            }));
          }
        }
      } catch (err) {
        console.error('Failed to load locations', err);
      } finally {
        if (isMounted) setLoadingLocations(false);
      }
    }

    loadLocations();
    return () => {
      isMounted = false;
    };
  }, [initialValues]);

  const validateForm = (): boolean => {
    const newErrors: FormValidationErrors = {};

    // 1. Area validation
    if (!formData.area_sqft || isNaN(formData.area_sqft)) {
      newErrors.area_sqft = 'Carpet area is required.';
    } else if (formData.area_sqft <= 0) {
      newErrors.area_sqft = 'Carpet area must be greater than 0 sq ft.';
    } else if (formData.area_sqft > 50000) {
      newErrors.area_sqft = 'Carpet area cannot exceed 50,000 sq ft.';
    }

    // 2. BHK validation
    if (!formData.bhk || formData.bhk < 1) {
      newErrors.bhk = 'BHK must be at least 1.';
    } else if (formData.bhk > 20) {
      newErrors.bhk = 'BHK cannot exceed 20.';
    }

    // 3. Bathroom validation
    if (!formData.bathroom || formData.bathroom < 1) {
      newErrors.bathroom = 'At least 1 bathroom is required.';
    } else if (formData.bathroom > 20) {
      newErrors.bathroom = 'Bathrooms cannot exceed 20.';
    }

    // 4. Balcony validation
    if (formData.balcony === undefined || formData.balcony < 0) {
      newErrors.balcony = 'Balconies cannot be negative.';
    } else if (formData.balcony > 20) {
      newErrors.balcony = 'Balconies cannot exceed 20.';
    }

    // 5. Floor validation
    if (formData.floor_num === undefined || isNaN(formData.floor_num)) {
      newErrors.floor_num = 'Floor number is required.';
    } else if (formData.floor_num < -5 || formData.floor_num > 200) {
      newErrors.floor_num = 'Floor number must be between -5 and 200.';
    }

    // 6. Total floors validation
    if (!formData.total_floors || formData.total_floors < 1) {
      newErrors.total_floors = 'Total floors must be at least 1.';
    } else if (formData.total_floors > 200) {
      newErrors.total_floors = 'Total floors cannot exceed 200.';
    }

    // 7. Floor vs Total floors logical constraint
    if (
      formData.floor_num > 0 &&
      formData.total_floors > 0 &&
      formData.floor_num > formData.total_floors
    ) {
      newErrors.floor_num = `Floor (${formData.floor_num}) cannot exceed total floors (${formData.total_floors}).`;
    }

    // 8. Location validation
    if (!formData.location || formData.location.trim() === '') {
      newErrors.location = 'Please select a valid location.';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;
    const parsedValue =
      type === 'number' ? (value === '' ? '' : Number(value)) : value;

    setFormData((prev) => ({
      ...prev,
      [name]: parsedValue,
    }));

    // Clear specific field error on edit
    if (errors[name as keyof FormValidationErrors]) {
      setErrors((prev) => ({
        ...prev,
        [name]: undefined,
      }));
    }
    if (apiError) setApiError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setApiError(null);

    if (!validateForm()) {
      return;
    }

    try {
      setIsSubmitting(true);
      const predictionResponse = await predictionClient.predict(formData);

      // Transition smoothly to /result with prediction payload
      navigate('/result', {
        state: {
          inputs: formData,
          result: predictionResponse,
          timestamp: new Date().toISOString(),
        },
      });
    } catch (err: unknown) {
      if (err instanceof Error) {
        setApiError(err.message);
      } else {
        setApiError('Unable to generate valuation. Please verify inputs and try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const locationOptions: SelectOption[] = locations.map((loc) => ({
    value: loc,
    label: formatLocation(loc),
  }));

  return (
    <form onSubmit={handleSubmit} className="space-y-6 sm:space-y-8" noValidate>
      {/* Error Notification Banner */}
      {apiError && (
        <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-900 flex items-start space-x-3 shadow-xs animate-fade-in-up">
          <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
          <div className="flex-1">
            <h4 className="text-sm font-bold text-rose-900">
              Valuation Request Failed
            </h4>
            <p className="text-xs text-rose-700 mt-1 leading-relaxed">
              {apiError}
            </p>
          </div>
        </div>
      )}

      {/* Section 1: Location & Core Dimensions */}
      <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200/80 shadow-soft transition-all hover:shadow-card">
        <div className="flex items-center space-x-3 pb-4 mb-6 border-b border-slate-100">
          <div className="w-8 h-8 rounded-lg bg-brand-50 text-brand-600 flex items-center justify-center font-bold text-sm">
            1
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900">
              Location & Spatial Dimensions
            </h3>
            <p className="text-xs text-slate-500">
              Target metropolitan market and carpet area parameters
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 sm:gap-6">
          <div className="md:col-span-1">
            <SelectField
              label="City / Market"
              name="location"
              required
              value={formData.location}
              onChange={handleInputChange}
              options={
                loadingLocations
                  ? [{ value: '', label: 'Loading verified cities...' }]
                  : locationOptions
              }
              icon={<MapPin className="w-4 h-4" />}
              error={errors.location}
              disabled={loadingLocations || isSubmitting}
            />
          </div>

          <div className="md:col-span-1">
            <InputField
              label="Carpet Area"
              name="area_sqft"
              type="number"
              required
              min={1}
              max={50000}
              step={10}
              unit="sq ft"
              placeholder="e.g. 1200"
              value={formData.area_sqft}
              onChange={handleInputChange}
              icon={<Maximize2 className="w-4 h-4" />}
              error={errors.area_sqft}
              disabled={isSubmitting}
            />
          </div>

          <div className="md:col-span-1">
            <InputField
              label="Bedrooms (BHK)"
              name="bhk"
              type="number"
              required
              min={1}
              max={20}
              unit="BHK"
              placeholder="e.g. 2 or 3"
              value={formData.bhk}
              onChange={handleInputChange}
              icon={<BedDouble className="w-4 h-4" />}
              error={errors.bhk}
              disabled={isSubmitting}
            />
          </div>
        </div>
      </div>

      {/* Section 2: Space & Floor Specifications */}
      <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200/80 shadow-soft transition-all hover:shadow-card">
        <div className="flex items-center space-x-3 pb-4 mb-6 border-b border-slate-100">
          <div className="w-8 h-8 rounded-lg bg-brand-50 text-brand-600 flex items-center justify-center font-bold text-sm">
            2
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900">
              Floor & Layout Specifications
            </h3>
            <p className="text-xs text-slate-500">
              Vertical level within building and room layout counts
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 sm:gap-6">
          <InputField
            label="Bathrooms"
            name="bathroom"
            type="number"
            required
            min={1}
            max={20}
            placeholder="e.g. 2"
            value={formData.bathroom}
            onChange={handleInputChange}
            icon={<Bath className="w-4 h-4" />}
            error={errors.bathroom}
            disabled={isSubmitting}
          />

          <InputField
            label="Balconies"
            name="balcony"
            type="number"
            min={0}
            max={20}
            placeholder="e.g. 1"
            value={formData.balcony}
            onChange={handleInputChange}
            icon={<Layers className="w-4 h-4" />}
            error={errors.balcony}
            disabled={isSubmitting}
          />

          <InputField
            label="Property Floor"
            name="floor_num"
            type="number"
            min={-5}
            max={200}
            helperText="0 for Ground, -1 for Basement"
            value={formData.floor_num}
            onChange={handleInputChange}
            icon={<Building className="w-4 h-4" />}
            error={errors.floor_num}
            disabled={isSubmitting}
          />

          <InputField
            label="Total Building Floors"
            name="total_floors"
            type="number"
            min={1}
            max={200}
            placeholder="e.g. 10"
            value={formData.total_floors}
            onChange={handleInputChange}
            icon={<Layers className="w-4 h-4" />}
            error={errors.total_floors}
            disabled={isSubmitting}
          />
        </div>
      </div>

      {/* Section 3: Property & Transaction Metadata */}
      <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200/80 shadow-soft transition-all hover:shadow-card">
        <div className="flex items-center space-x-3 pb-4 mb-6 border-b border-slate-100">
          <div className="w-8 h-8 rounded-lg bg-brand-50 text-brand-600 flex items-center justify-center font-bold text-sm">
            3
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900">
              Property & Transaction Specifications
            </h3>
            <p className="text-xs text-slate-500">
              Furnishing status, legal ownership, and orientation attributes
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 sm:gap-6">
          <SelectField
            label="Furnishing Status"
            name="Furnishing"
            value={formData.Furnishing}
            onChange={handleInputChange}
            options={FURNISHING_OPTIONS}
            icon={<KeyRound className="w-4 h-4" />}
            error={errors.Furnishing}
            disabled={isSubmitting}
          />

          <SelectField
            label="Transaction Type"
            name="Transaction"
            value={formData.Transaction}
            onChange={handleInputChange}
            options={TRANSACTION_OPTIONS}
            icon={<FileText className="w-4 h-4" />}
            error={errors.Transaction}
            disabled={isSubmitting}
          />

          <SelectField
            label="Facing Direction"
            name="facing"
            value={formData.facing}
            onChange={handleInputChange}
            options={FACING_OPTIONS}
            icon={<Compass className="w-4 h-4" />}
            error={errors.facing}
            disabled={isSubmitting}
          />

          <SelectField
            label="Ownership Type"
            name="Ownership"
            value={formData.Ownership}
            onChange={handleInputChange}
            options={OWNERSHIP_OPTIONS}
            icon={<CheckCircle2 className="w-4 h-4" />}
            error={errors.Ownership}
            disabled={isSubmitting}
          />
        </div>
      </div>

      {/* Submit CTA Section */}
      <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="text-xs text-slate-500 flex items-center space-x-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
          <span>Inputs verified in real-time</span>
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className={`
            w-full sm:w-auto px-8 py-4 rounded-xl font-bold text-sm text-white shadow-md
            transition-all duration-200 ease-out flex items-center justify-center space-x-2.5 cursor-pointer
            ${
              isSubmitting
                ? 'bg-brand-500 cursor-wait opacity-90'
                : 'bg-brand-600 hover:bg-brand-700 hover:shadow-lg hover:shadow-brand-600/25 active:scale-[0.98]'
            }
          `}
        >
          {isSubmitting ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Analyzing Property Specifications...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4 text-brand-200" />
              <span>Estimate Property Value</span>
            </>
          )}
        </button>
      </div>
    </form>
  );
};

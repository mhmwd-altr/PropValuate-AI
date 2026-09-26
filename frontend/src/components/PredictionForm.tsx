import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  MapPin, Maximize2, BedDouble, Bath, Layers, Sparkles, Compass,
  KeyRound, FileText, Building, AlertTriangle, Loader2, CheckCircle2,
  Zap, ShieldCheck, User, ToggleLeft, ToggleRight,
} from 'lucide-react';
import { PredictionRequest, PredictionRequestV2, FormValidationErrors } from '../types/prediction';
import { predictionClient } from '../api/predictionClient';
import { formatLocation } from '../utils/formatters';
import { InputField } from './InputField';
import { SelectField, SelectOption } from './SelectField';
import { getCityCoord } from '../data/cityCoordinates';

interface PredictionFormProps {
  initialValues?: PredictionRequest;
  initialV2Values?: PredictionRequestV2;
  defaultMode?: 'v1' | 'v2';
}

const DEFAULT_FORM_VALUES: PredictionRequest = {
  area_sqft: 1200, bhk: 2, bathroom: 2, balcony: 1, floor_num: 3, total_floors: 10,
  location: 'bangalore', Furnishing: 'Semi-Furnished', Transaction: 'Resale',
  facing: 'East', Ownership: 'Freehold',
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
  { value: 'East', label: 'East' }, { value: 'North - East', label: 'North - East' },
  { value: 'North', label: 'North' }, { value: 'West', label: 'West' },
  { value: 'South', label: 'South' }, { value: 'North - West', label: 'North - West' },
  { value: 'South - East', label: 'South - East' }, { value: 'South -West', label: 'South - West' },
];

const OWNERSHIP_OPTIONS: SelectOption[] = [
  { value: 'Freehold', label: 'Freehold' }, { value: 'Leasehold', label: 'Leasehold' },
  { value: 'Co-operative Society', label: 'Co-operative Society' },
  { value: 'Power Of Attorney', label: 'Power Of Attorney' },
];

const DEFAULT_V2_VALUES: PredictionRequestV2 = {
  area_sqft: 1500, bhk: 3, latitude: 12.9716, longitude: 77.5946,
  city: 'bangalore', posted_by: 'Owner', rera: 1,
  under_construction: 0, ready_to_move: 1, resale: 1, is_rk: 0,
};

const POSTED_BY_OPTIONS: SelectOption[] = [
  { value: 'Owner', label: 'Owner' },
  { value: 'Dealer', label: 'Dealer' },
  { value: 'Builder', label: 'Builder' },
];

export const PredictionForm: React.FC<PredictionFormProps> = ({
  initialValues, initialV2Values, defaultMode = 'v2',
}) => {
  const navigate = useNavigate();
  const [mode, setMode] = useState<'v1' | 'v2'>(defaultMode);
  const [formData, setFormData] = useState<PredictionRequest>(initialValues || DEFAULT_FORM_VALUES);
  const [errors, setErrors] = useState<FormValidationErrors>({});
  const [formDataV2, setFormDataV2] = useState<PredictionRequestV2>(initialV2Values || DEFAULT_V2_VALUES);
  const [errorsV2, setErrorsV2] = useState<Partial<Record<keyof PredictionRequestV2, string>>>({});
  const [locations, setLocations] = useState<string[]>([]);
  const [loadingLocations, setLoadingLocations] = useState<boolean>(true);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [apiError, setApiError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    async function loadLocations() {
      try {
        setLoadingLocations(true);
        const locs = await predictionClient.getLocations();
        if (isMounted) {
          const sorted = [...locs].sort((a, b) => a.localeCompare(b));
          setLocations(sorted);
          if (sorted.length > 0) {
            if (!initialValues) {
              setFormData((prev) => ({ ...prev, location: prev.location || sorted[0] }));
            }
            if (!initialV2Values) {
              const defaultCity = sorted.includes('bangalore') ? 'bangalore' : sorted[0];
              const coord = getCityCoord(defaultCity);
              setFormDataV2((prev) => ({
                ...prev, city: defaultCity,
                latitude: coord?.lat ?? prev.latitude,
                longitude: coord?.lon ?? prev.longitude,
              }));
            }
          }
        }
      } catch (err) {
        console.error('Failed to load locations', err);
      } finally {
        if (isMounted) setLoadingLocations(false);
      }
    }
    loadLocations();
    return () => { isMounted = false; };
  }, [initialValues, initialV2Values]);

  const validateFormV1 = (): boolean => {
    const newErrors: FormValidationErrors = {};
    if (!formData.area_sqft || isNaN(formData.area_sqft)) newErrors.area_sqft = 'Carpet area is required.';
    else if (formData.area_sqft <= 0) newErrors.area_sqft = 'Carpet area must be greater than 0 sq ft.';
    else if (formData.area_sqft > 50000) newErrors.area_sqft = 'Carpet area cannot exceed 50,000 sq ft.';
    if (!formData.bhk || formData.bhk < 1) newErrors.bhk = 'BHK must be at least 1.';
    else if (formData.bhk > 20) newErrors.bhk = 'BHK cannot exceed 20.';
    if (!formData.bathroom || formData.bathroom < 1) newErrors.bathroom = 'At least 1 bathroom is required.';
    else if (formData.bathroom > 20) newErrors.bathroom = 'Bathrooms cannot exceed 20.';
    if (formData.balcony === undefined || formData.balcony < 0) newErrors.balcony = 'Balconies cannot be negative.';
    else if (formData.balcony > 20) newErrors.balcony = 'Balconies cannot exceed 20.';
    if (formData.floor_num === undefined || isNaN(formData.floor_num)) newErrors.floor_num = 'Floor number is required.';
    else if (formData.floor_num < -5 || formData.floor_num > 200) newErrors.floor_num = 'Floor number must be between -5 and 200.';
    if (!formData.total_floors || formData.total_floors < 1) newErrors.total_floors = 'Total floors must be at least 1.';
    else if (formData.total_floors > 200) newErrors.total_floors = 'Total floors cannot exceed 200.';
    if (formData.floor_num > 0 && formData.total_floors > 0 && formData.floor_num > formData.total_floors)
      newErrors.floor_num = `Floor (${formData.floor_num}) cannot exceed total floors (${formData.total_floors}).`;
    if (!formData.location || formData.location.trim() === '') newErrors.location = 'Please select a valid location.';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const parsedValue = type === 'number' ? (value === '' ? '' : Number(value)) : value;
    setFormData((prev) => ({ ...prev, [name]: parsedValue }));
    if (errors[name as keyof FormValidationErrors]) setErrors((prev) => ({ ...prev, [name]: undefined }));
    if (apiError) setApiError(null);
  };

  const handleSubmitV1 = async (e: React.FormEvent) => {
    e.preventDefault(); setApiError(null);
    if (!validateFormV1()) return;
    try {
      setIsSubmitting(true);
      const predictionResponse = await predictionClient.predict(formData);
      navigate('/result', { state: { inputs: formData, result: predictionResponse, timestamp: new Date().toISOString() } });
    } catch (err: unknown) {
      setApiError(err instanceof Error ? err.message : 'Unable to generate valuation. Please verify inputs and try again.');
    } finally { setIsSubmitting(false); }
  };

  const validateFormV2 = (): boolean => {
    const newErrors: Partial<Record<keyof PredictionRequestV2, string>> = {};

    // 1. area_sqft: > 0 and <= 50000
    if (!formDataV2.area_sqft || isNaN(formDataV2.area_sqft) || formDataV2.area_sqft <= 0) {
      newErrors.area_sqft = 'Carpet area must be greater than 0 sq ft.';
    } else if (formDataV2.area_sqft > 50000) {
      newErrors.area_sqft = 'Carpet area cannot exceed 50,000 sq ft.';
    }

    // 2. bhk: integer 1-20
    if (!formDataV2.bhk || isNaN(formDataV2.bhk) || !Number.isInteger(Number(formDataV2.bhk)) || formDataV2.bhk < 1) {
      newErrors.bhk = 'BHK must be an integer of at least 1.';
    } else if (formDataV2.bhk > 20) {
      newErrors.bhk = 'BHK cannot exceed 20.';
    }

    // 3. city & coordinates: required, in registry, lat 6-38, lon 68-98
    if (!formDataV2.city || formDataV2.city.trim() === '') {
      newErrors.city = 'Please select a valid city.';
    } else {
      const coord = getCityCoord(formDataV2.city);
      if (!coord) {
        newErrors.city = 'Selected city has no coordinate mapping in the 81-city registry.';
      } else if (
        !Number.isFinite(coord.lat) ||
        !Number.isFinite(coord.lon) ||
        coord.lat < 6.0 ||
        coord.lat > 38.0 ||
        coord.lon < 68.0 ||
        coord.lon > 98.0
      ) {
        newErrors.city = 'City coordinates are outside supported Indian geographical bounds (Lat: 6–38, Lon: 68–98).';
      }
    }

    // 4. posted_by: Owner | Dealer | Builder
    if (!formDataV2.posted_by || !['Owner', 'Dealer', 'Builder'].includes(formDataV2.posted_by)) {
      newErrors.posted_by = 'Posted by must be Owner, Dealer, or Builder.';
    }

    setErrorsV2(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChangeV2 = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const parsedValue = type === 'number' ? (value === '' ? '' : Number(value)) : value;
    setFormDataV2((prev) => ({ ...prev, [name]: parsedValue }));
    if (errorsV2[name as keyof PredictionRequestV2]) setErrorsV2((prev) => ({ ...prev, [name]: undefined }));
    if (apiError) setApiError(null);
  };

  const handleCityChangeV2 = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const city = e.target.value;
    const coord = getCityCoord(city);
    setFormDataV2((prev) => ({
      ...prev,
      city,
      latitude: coord ? coord.lat : NaN,
      longitude: coord ? coord.lon : NaN,
    }));
    if (errorsV2.city) setErrorsV2((prev) => ({ ...prev, city: undefined }));
    if (apiError) setApiError(null);
  };

  const handlePropertyStatusChange = (status: 'ready' | 'construction') => {
    setFormDataV2((prev) => ({
      ...prev,
      ready_to_move: status === 'ready' ? 1 : 0,
      under_construction: status === 'construction' ? 1 : 0,
    }));
  };

  const handleSubmitV2 = async (e: React.FormEvent) => {
    e.preventDefault();
    setApiError(null);
    if (!validateFormV2()) return;

    const coord = getCityCoord(formDataV2.city);
    if (!coord) {
      setErrorsV2((prev) => ({
        ...prev,
        city: 'Selected city has no coordinate mapping in the 81-city registry.',
      }));
      return;
    }

    // Build strict payload with exact raw fields
    const payload: PredictionRequestV2 = {
      area_sqft: Number(formDataV2.area_sqft),
      bhk: Math.floor(Number(formDataV2.bhk)),
      latitude: coord.lat,
      longitude: coord.lon,
      city: formDataV2.city.toLowerCase().trim(),
      posted_by: formDataV2.posted_by,
      rera: formDataV2.rera === 1 ? 1 : 0,
      under_construction: formDataV2.under_construction === 1 ? 1 : 0,
      ready_to_move: formDataV2.ready_to_move === 1 ? 1 : 0,
      resale: formDataV2.resale === 1 ? 1 : 0,
      is_rk: formDataV2.is_rk === 1 ? 1 : 0,
    };

    try {
      setIsSubmitting(true);
      const v2Response = await predictionClient.predictV2(payload);
      const compatInputs: PredictionRequest = {
        area_sqft: payload.area_sqft,
        bhk: payload.bhk,
        bathroom: 2,
        balcony: 0,
        floor_num: 0,
        total_floors: 1,
        location: payload.city,
        Furnishing: 'N/A',
        Transaction: payload.resale ? 'Resale' : 'New Property',
        facing: 'N/A',
        Ownership: 'N/A',
      };
      const compatResult = {
        predicted_price: v2Response.predicted_price,
        predicted_price_lakhs: v2Response.predicted_price_lakhs,
        currency: v2Response.currency,
        status: v2Response.status,
      };
      navigate('/result', {
        state: {
          inputs: compatInputs,
          result: compatResult,
          timestamp: new Date().toISOString(),
          inputsV2: payload,
          resultV2: v2Response,
        },
      });
    } catch (err: unknown) {
      setApiError(
        err instanceof Error
          ? err.message
          : 'Unable to generate V2 valuation. Please verify inputs and try again.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const locationOptions: SelectOption[] = locations.map((loc) => ({ value: loc, label: formatLocation(loc) }));
  const loadingOption = [{ value: '', label: 'Loading verified cities...' }];

  const errorBanner = apiError && (
    <div className='p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-900 flex items-start space-x-3 shadow-xs animate-fade-in-up'>
      <AlertTriangle className='w-5 h-5 text-rose-600 shrink-0 mt-0.5' />
      <div className='flex-1'>
        <h4 className='text-sm font-bold text-rose-900'>Valuation Request Failed</h4>
        <p className='text-xs text-rose-700 mt-1 leading-relaxed'>{apiError}</p>
      </div>
    </div>
  );

  const v1BtnClass = `w-full sm:w-auto px-8 py-4 rounded-xl font-bold text-sm text-white shadow-md transition-all duration-200 ease-out flex items-center justify-center space-x-2.5 cursor-pointer ${isSubmitting ? 'bg-brand-500 cursor-wait opacity-90' : 'bg-brand-600 hover:bg-brand-700 hover:shadow-lg hover:shadow-brand-600/25 active:scale-[0.98]'}`;
  const v2BtnClass = `w-full sm:w-auto px-8 py-4 rounded-xl font-bold text-sm text-white shadow-md transition-all duration-200 ease-out flex items-center justify-center space-x-2.5 cursor-pointer ${isSubmitting ? 'bg-indigo-500 cursor-wait opacity-90' : 'bg-indigo-600 hover:bg-indigo-700 hover:shadow-lg hover:shadow-indigo-600/25 active:scale-[0.98]'}`;

  const SectionHdr = ({ num, title, sub, v2 }: { num: number; title: string; sub: string; v2?: boolean }) => (
    <div className='flex items-center space-x-3 pb-4 mb-6 border-b border-slate-100'>
      <div className={`w-8 h-8 rounded-lg ${v2 ? 'bg-indigo-50 text-indigo-600' : 'bg-brand-50 text-brand-600'} flex items-center justify-center font-bold text-sm`}>{num}</div>
      <div>
        <h3 className='text-base font-bold text-slate-900'>{title}</h3>
        <p className='text-xs text-slate-500'>{sub}</p>
      </div>
    </div>
  );

  const renderV1Form = () => (
    <form onSubmit={handleSubmitV1} className='space-y-6 sm:space-y-8' noValidate>
      {errorBanner}
      <div className='bg-white rounded-2xl p-6 sm:p-8 border border-slate-200/80 shadow-soft transition-all hover:shadow-card'>
        <SectionHdr num={1} title='Location & Spatial Dimensions' sub='Target metropolitan market and carpet area parameters' />
        <div className='grid grid-cols-1 md:grid-cols-3 gap-5 sm:gap-6'>
          <div className='md:col-span-1'>
            <SelectField label='City / Market' name='location' required value={formData.location} onChange={handleInputChange}
              options={loadingLocations ? loadingOption : locationOptions}
              icon={<MapPin className='w-4 h-4' />} error={errors.location} disabled={loadingLocations || isSubmitting} />
          </div>
          <div className='md:col-span-1'>
            <InputField label='Carpet Area' name='area_sqft' type='number' required min={1} max={50000} step={10} unit='sq ft'
              placeholder='e.g. 1200' value={formData.area_sqft} onChange={handleInputChange}
              icon={<Maximize2 className='w-4 h-4' />} error={errors.area_sqft} disabled={isSubmitting} />
          </div>
          <div className='md:col-span-1'>
            <InputField label='Bedrooms (BHK)' name='bhk' type='number' required min={1} max={20} unit='BHK'
              placeholder='e.g. 2 or 3' value={formData.bhk} onChange={handleInputChange}
              icon={<BedDouble className='w-4 h-4' />} error={errors.bhk} disabled={isSubmitting} />
          </div>
        </div>
      </div>
      <div className='bg-white rounded-2xl p-6 sm:p-8 border border-slate-200/80 shadow-soft transition-all hover:shadow-card'>
        <SectionHdr num={2} title='Floor & Layout Specifications' sub='Vertical level within building and room layout counts' />
        <div className='grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 sm:gap-6'>
          <InputField label='Bathrooms' name='bathroom' type='number' required min={1} max={20} placeholder='e.g. 2' value={formData.bathroom} onChange={handleInputChange} icon={<Bath className='w-4 h-4' />} error={errors.bathroom} disabled={isSubmitting} />
          <InputField label='Balconies' name='balcony' type='number' min={0} max={20} placeholder='e.g. 1' value={formData.balcony} onChange={handleInputChange} icon={<Layers className='w-4 h-4' />} error={errors.balcony} disabled={isSubmitting} />
          <InputField label='Property Floor' name='floor_num' type='number' min={-5} max={200} helperText='0 for Ground, -1 for Basement' value={formData.floor_num} onChange={handleInputChange} icon={<Building className='w-4 h-4' />} error={errors.floor_num} disabled={isSubmitting} />
          <InputField label='Total Building Floors' name='total_floors' type='number' min={1} max={200} placeholder='e.g. 10' value={formData.total_floors} onChange={handleInputChange} icon={<Layers className='w-4 h-4' />} error={errors.total_floors} disabled={isSubmitting} />
        </div>
      </div>
      <div className='bg-white rounded-2xl p-6 sm:p-8 border border-slate-200/80 shadow-soft transition-all hover:shadow-card'>
        <SectionHdr num={3} title='Property & Transaction Specifications' sub='Furnishing status, legal ownership, and orientation attributes' />
        <div className='grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 sm:gap-6'>
          <SelectField label='Furnishing Status' name='Furnishing' value={formData.Furnishing} onChange={handleInputChange} options={FURNISHING_OPTIONS} icon={<KeyRound className='w-4 h-4' />} error={errors.Furnishing} disabled={isSubmitting} />
          <SelectField label='Transaction Type' name='Transaction' value={formData.Transaction} onChange={handleInputChange} options={TRANSACTION_OPTIONS} icon={<FileText className='w-4 h-4' />} error={errors.Transaction} disabled={isSubmitting} />
          <SelectField label='Facing Direction' name='facing' value={formData.facing} onChange={handleInputChange} options={FACING_OPTIONS} icon={<Compass className='w-4 h-4' />} error={errors.facing} disabled={isSubmitting} />
          <SelectField label='Ownership Type' name='Ownership' value={formData.Ownership} onChange={handleInputChange} options={OWNERSHIP_OPTIONS} icon={<CheckCircle2 className='w-4 h-4' />} error={errors.Ownership} disabled={isSubmitting} />
        </div>
      </div>
      <div className='pt-2 flex flex-col sm:flex-row items-center justify-between gap-4'>
        <div className='text-xs text-slate-500 flex items-center space-x-2'>
          <span className='w-2 h-2 rounded-full bg-emerald-500'></span>
          <span>Inputs verified in real-time</span>
        </div>
        <button type='submit' disabled={isSubmitting} className={v1BtnClass}>
          {isSubmitting ? (<><Loader2 className='w-4 h-4 animate-spin' /><span>Analyzing Property Specifications...</span></>) : (<><Sparkles className='w-4 h-4 text-brand-200' /><span>Estimate Property Value</span></>)}
        </button>
      </div>
    </form>
  );

  const renderV2Form = () => (
    <form onSubmit={handleSubmitV2} className='space-y-6 sm:space-y-8' noValidate>
      {errorBanner}
      <div className='bg-white rounded-2xl p-6 sm:p-8 border border-slate-200/80 shadow-soft transition-all hover:shadow-card'>
        <SectionHdr num={1} title='City & Core Dimensions' sub='Metropolitan market, carpet area, and bedroom count' v2 />
        <div className='grid grid-cols-1 md:grid-cols-3 gap-5 sm:gap-6'>
          <div className='md:col-span-1'>
            <SelectField label='City / Market' name='city' required value={formDataV2.city} onChange={handleCityChangeV2}
              options={loadingLocations ? loadingOption : locationOptions}
              icon={<MapPin className='w-4 h-4' />} error={errorsV2.city} disabled={loadingLocations || isSubmitting} />
          </div>
          <div className='md:col-span-1'>
            <InputField label='Carpet Area' name='area_sqft' type='number' required min={1} max={50000} step={10} unit='sq ft'
              placeholder='e.g. 1500' value={formDataV2.area_sqft} onChange={handleInputChangeV2}
              icon={<Maximize2 className='w-4 h-4' />} error={errorsV2.area_sqft} disabled={isSubmitting} />
          </div>
          <div className='md:col-span-1'>
            <InputField label='Bedrooms (BHK)' name='bhk' type='number' required min={1} max={20} unit='BHK'
              placeholder='e.g. 3' value={formDataV2.bhk} onChange={handleInputChangeV2}
              icon={<BedDouble className='w-4 h-4' />} error={errorsV2.bhk} disabled={isSubmitting} />
          </div>
        </div>
        <div className='mt-4 p-3 rounded-xl bg-indigo-50/60 border border-indigo-100 flex items-center space-x-2'>
          <MapPin className='w-3.5 h-3.5 text-indigo-500 shrink-0' />
          <span className='text-xs text-indigo-700'>
            <span className='font-semibold'>Geolocation:</span>{' '}
            {Number.isFinite(formDataV2.latitude) && Number.isFinite(formDataV2.longitude)
              ? `${formDataV2.latitude.toFixed(4)}°N, ${formDataV2.longitude.toFixed(4)}°E`
              : 'Unresolved coordinate'}
            <span className='text-indigo-500 ml-1'>(auto-resolved from city centre)</span>
          </span>
        </div>
      </div>
      <div className='bg-white rounded-2xl p-6 sm:p-8 border border-slate-200/80 shadow-soft transition-all hover:shadow-card'>
        <SectionHdr num={2} title='Listing & Property Attributes' sub='Listing source, regulatory compliance, and transaction type' v2 />
        <div className='grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 sm:gap-6'>
          <SelectField label='Posted By' name='posted_by' value={formDataV2.posted_by} onChange={handleInputChangeV2} options={POSTED_BY_OPTIONS} icon={<User className='w-4 h-4' />} disabled={isSubmitting} />
          <div>
            <label className='block text-xs font-semibold text-slate-600 mb-2 uppercase tracking-wider'>RERA Status</label>
            <div className='flex gap-3'>
              <button type='button' onClick={() => setFormDataV2((p) => ({ ...p, rera: 1 }))}
                className={`flex-1 py-2.5 rounded-xl text-xs font-bold border transition-all ${formDataV2.rera === 1 ? 'bg-emerald-600 text-white border-emerald-600 shadow-sm' : 'bg-white text-slate-600 border-slate-200 hover:border-emerald-300'}`}>
                <ShieldCheck className='w-3.5 h-3.5 inline mr-1' />RERA
              </button>
              <button type='button' onClick={() => setFormDataV2((p) => ({ ...p, rera: 0 }))}
                className={`flex-1 py-2.5 rounded-xl text-xs font-bold border transition-all ${formDataV2.rera === 0 ? 'bg-slate-700 text-white border-slate-700 shadow-sm' : 'bg-white text-slate-600 border-slate-200 hover:border-slate-400'}`}>
                Non-RERA
              </button>
            </div>
          </div>
          <div>
            <label className='block text-xs font-semibold text-slate-600 mb-2 uppercase tracking-wider'>Transaction</label>
            <div className='flex gap-3'>
              <button type='button' onClick={() => setFormDataV2((p) => ({ ...p, resale: 1 }))}
                className={`flex-1 py-2.5 rounded-xl text-xs font-bold border transition-all ${formDataV2.resale === 1 ? 'bg-brand-600 text-white border-brand-600 shadow-sm' : 'bg-white text-slate-600 border-slate-200 hover:border-brand-300'}`}>
                Resale
              </button>
              <button type='button' onClick={() => setFormDataV2((p) => ({ ...p, resale: 0 }))}
                className={`flex-1 py-2.5 rounded-xl text-xs font-bold border transition-all ${formDataV2.resale === 0 ? 'bg-brand-600 text-white border-brand-600 shadow-sm' : 'bg-white text-slate-600 border-slate-200 hover:border-brand-300'}`}>
                New
              </button>
            </div>
          </div>
        </div>
        <div className='mt-5 sm:mt-6 grid grid-cols-1 sm:grid-cols-2 gap-5 sm:gap-6'>
          <div>
            <label className='block text-xs font-semibold text-slate-600 mb-2 uppercase tracking-wider'>Property Status</label>
            <div className='flex gap-3'>
              <button type='button' onClick={() => handlePropertyStatusChange('ready')}
                className={`flex-1 py-2.5 rounded-xl text-xs font-bold border transition-all ${formDataV2.ready_to_move === 1 ? 'bg-emerald-600 text-white border-emerald-600 shadow-sm' : 'bg-white text-slate-600 border-slate-200 hover:border-emerald-300'}`}>
                <Zap className='w-3.5 h-3.5 inline mr-1' />Ready to Move
              </button>
              <button type='button' onClick={() => handlePropertyStatusChange('construction')}
                className={`flex-1 py-2.5 rounded-xl text-xs font-bold border transition-all ${formDataV2.under_construction === 1 ? 'bg-amber-600 text-white border-amber-600 shadow-sm' : 'bg-white text-slate-600 border-slate-200 hover:border-amber-300'}`}>
                Under Construction
              </button>
            </div>
          </div>
          <div>
            <label className='block text-xs font-semibold text-slate-600 mb-2 uppercase tracking-wider'>Layout Type</label>
            <div className='flex gap-3'>
              <button type='button' onClick={() => setFormDataV2((p) => ({ ...p, is_rk: 0 }))}
                className={`flex-1 py-2.5 rounded-xl text-xs font-bold border transition-all ${formDataV2.is_rk === 0 ? 'bg-brand-600 text-white border-brand-600 shadow-sm' : 'bg-white text-slate-600 border-slate-200 hover:border-brand-300'}`}>
                Standard BHK
              </button>
              <button type='button' onClick={() => setFormDataV2((p) => ({ ...p, is_rk: 1 }))}
                className={`flex-1 py-2.5 rounded-xl text-xs font-bold border transition-all ${formDataV2.is_rk === 1 ? 'bg-slate-700 text-white border-slate-700 shadow-sm' : 'bg-white text-slate-600 border-slate-200 hover:border-slate-400'}`}>
                RK Studio
              </button>
            </div>
          </div>
        </div>
      </div>
      <div className='pt-2 flex flex-col sm:flex-row items-center justify-between gap-4'>
        <div className='text-xs text-indigo-600 flex items-center space-x-2 font-medium'>
          <span className='w-2 h-2 rounded-full bg-indigo-500 animate-pulse'></span>
          <span>Geospatial features engineered by V2 model backend</span>
        </div>
        <button type='submit' disabled={isSubmitting} className={v2BtnClass}>
          {isSubmitting ? (<><Loader2 className='w-4 h-4 animate-spin' /><span>Running V2 Inference...</span></>) : (<><Zap className='w-4 h-4 text-indigo-200' /><span>Estimate with V2 Engine</span></>)}
        </button>
      </div>
    </form>
  );

  return (
    <div className='space-y-6 sm:space-y-8'>
      <div className='bg-white rounded-2xl p-4 border border-slate-200/80 shadow-soft'>
        <div className='flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3'>
          <div>
            <h3 className='text-sm font-bold text-slate-800'>Valuation Engine</h3>
            <p className='text-xs text-slate-500 mt-0.5'>
              {mode === 'v2'
                ? 'V2 — HistGradientBoosting with geospatial features (recommended)'
                : 'V1 — Baseline model (legacy)'}
            </p>
          </div>
          <div className='flex items-center gap-3'>
            <span className={`text-xs font-semibold ${mode === 'v1' ? 'text-slate-800' : 'text-slate-400'}`}>V1 Baseline</span>
            <button
              type='button'
              id='engine-mode-toggle'
              onClick={() => { setMode(mode === 'v2' ? 'v1' : 'v2'); setApiError(null); }}
              className='relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none cursor-pointer'
              style={{ backgroundColor: mode === 'v2' ? 'rgb(79,70,229)' : 'rgb(203,213,225)' }}
              aria-label={`Switch to ${mode === 'v2' ? 'V1' : 'V2'} engine`}
            >
              <span className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform duration-200 ${mode === 'v2' ? 'translate-x-6' : 'translate-x-1'}`} />
            </button>
            <span className={`text-xs font-semibold ${mode === 'v2' ? 'text-indigo-700' : 'text-slate-400'}`}>
              V2 <span className='hidden sm:inline text-indigo-500'>(Recommended)</span>
            </span>
            {mode === 'v2' ? (<ToggleRight className='w-4 h-4 text-indigo-600' />) : (<ToggleLeft className='w-4 h-4 text-slate-400' />)}
          </div>
        </div>
      </div>
      {mode === 'v2' ? renderV2Form() : renderV1Form()}
    </div>
  );
};

// ─── Baseline (V1) Types ────────────────────────────────────────────────────

export interface PredictionRequest {
  area_sqft: number;
  bhk: number;
  bathroom: number;
  balcony: number;
  floor_num: number;
  total_floors: number;
  location: string;
  Furnishing: string;
  Transaction: string;
  facing: string;
  Ownership: string;
}

export interface PredictionResponse {
  predicted_price: number;
  predicted_price_lakhs: number;
  currency: string;
  status: string;
}

export interface LocationsResponse {
  total_locations: number;
  locations: string[];
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  locations_loaded: boolean;
  version: string;
}

export interface FormValidationErrors {
  area_sqft?: string;
  bhk?: string;
  bathroom?: string;
  balcony?: string;
  floor_num?: string;
  total_floors?: string;
  location?: string;
  Furnishing?: string;
  Transaction?: string;
  facing?: string;
  Ownership?: string;
  general?: string;
}

export interface ValuationResultState {
  inputs: PredictionRequest;
  result: PredictionResponse;
  timestamp: string;
  // Optional V2 parallel payload — populated only when V2 was used
  inputsV2?: PredictionRequestV2;
  resultV2?: PredictionResponseV2;
}

// ─── V2 Types ────────────────────────────────────────────────────────────────

/**
 * POST /api/v2/predict request body.
 * Mirrors backend PredictionRequestV2 (prediction_v2.py).
 */
export interface PredictionRequestV2 {
  area_sqft: number;
  bhk: number;
  latitude: number;
  longitude: number;
  city: string;
  posted_by: 'Owner' | 'Dealer' | 'Builder';
  rera: 0 | 1;
  under_construction: 0 | 1;
  ready_to_move: 0 | 1;
  resale: 0 | 1;
  is_rk: 0 | 1;
}

/**
 * Engineered feature metadata returned by V2 endpoint.
 * Mirrors backend EngineeredFeaturesMetadata.
 */
export interface EngineeredFeaturesMetadata {
  area_per_bhk: number;
  dist_nearest_metro_km: number;
  dist_mumbai_km: number;
  dist_delhi_km: number;
  dist_bangalore_km: number;
  city_grouped: string;
}

/**
 * POST /api/v2/predict response body.
 * Mirrors backend PredictionResponseV2 (prediction_v2.py).
 */
export interface PredictionResponseV2 {
  status: string;
  predicted_price: number;
  predicted_price_lakhs: number;
  currency: string;
  model_version: string;
  model_name: string;
  engineered_features?: EngineeredFeaturesMetadata;
}

/** Validation errors specific to V2 form fields */
export interface FormValidationErrorsV2 {
  area_sqft?: string;
  bhk?: string;
  city?: string;
  posted_by?: string;
  general?: string;
}


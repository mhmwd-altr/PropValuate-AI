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
}

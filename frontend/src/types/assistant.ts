export type AssistantIntent =
  | 'VALUATION_REQUEST'
  | 'PROPERTY_INPUT_CLARIFICATION'
  | 'VALUATION_EXPLANATION'
  | 'SUPPORTED_LOCATION_QUERY'
  | 'GENERAL_REAL_ESTATE_QUESTION'
  | 'UNSUPPORTED_REQUEST';

export interface PropertySlotsState {
  area_sqft?: number | null;
  bhk?: number | null;
  latitude?: number | null;
  longitude?: number | null;
  city?: string | null;
  posted_by?: string | null;
  rera?: number | null;
  under_construction?: number | null;
  ready_to_move?: number | null;
  resale?: number | null;
  is_rk?: number | null;
}

export interface ValuationToolResult {
  predicted_price: number;
  predicted_price_lakhs: number;
  rate_per_sqft: number;
  currency: string;
  model_version: string;
  model_name: string;
  engineered_features?: {
    area_per_bhk: number;
    dist_nearest_metro_km: number;
    dist_mumbai_km: number;
    dist_delhi_km: number;
    dist_bangalore_km: number;
    city_grouped: string;
  };
  property_details?: {
    area_sqft: number;
    bhk: number;
    city: string;
    posted_by: string;
    rera: boolean;
    ready_to_move: boolean;
    resale: boolean;
    is_rk: boolean;
  };
}

export interface AssistantChatRequest {
  message: string;
  session_id?: string | null;
}

export interface AssistantChatResponse {
  session_id: string;
  reply: string;
  intent: AssistantIntent;
  tool_called?: string | null;
  tool_result?: ValuationToolResult | { locations: string[]; total_count: number } | null;
  slots: PropertySlotsState;
  missing_slots: string[];
  is_valuation_complete: boolean;
  model_name: string;
  created_at: string;
}

export interface AssistantResetResponse {
  session_id: string;
  status: string;
  message: string;
}

export interface AssistantHealthResponse {
  status: string;
  provider_type: string;
  model_loaded: boolean;
  model_path: string;
  active_sessions: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  intent?: AssistantIntent;
  toolCalled?: string | null;
  toolResult?: any;
  slots?: PropertySlotsState;
  missingSlots?: string[];
  isValuationComplete?: boolean;
}

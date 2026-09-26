import {
  PredictionRequest,
  PredictionResponse,
  PredictionRequestV2,
  PredictionResponseV2,
  LocationsResponse,
  HealthResponse,
} from '../types/prediction';
import fallbackLocationsData from '../data/locations.json';


const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
).replace(/\/+$/, '');

class PredictionClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  /**
   * Fetches the list of allowed locations from the backend API,
   * falling back to the bundled locations dataset if the API is offline.
   */
  async getLocations(): Promise<string[]> {
    try {
      const response = await fetch(`${this.baseUrl}/locations`, {
        method: 'GET',
        headers: {
          Accept: 'application/json',
        },
      });

      if (!response.ok) {
        console.warn(
          `[API Warning] /locations returned status ${response.status}. Using bundled locations.`
        );
        return fallbackLocationsData.locations || [];
      }

      const data: LocationsResponse = await response.json();
      if (Array.isArray(data.locations) && data.locations.length > 0) {
        return data.locations;
      }
      return fallbackLocationsData.locations || [];
    } catch (err) {
      console.warn(
        '[API Warning] Failed to reach /locations endpoint. Using bundled locations.',
        err
      );
      return fallbackLocationsData.locations || [];
    }
  }

  /**
   * Sends a validated property prediction request to the FastAPI backend.
   */
  async predict(request: PredictionRequest): Promise<PredictionResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        let errorMessage = `Server error (Status: ${response.status})`;
        try {
          const errorData = await response.json();
          if (errorData.detail) {
            if (typeof errorData.detail === 'string') {
              errorMessage = errorData.detail;
            } else if (Array.isArray(errorData.detail) && errorData.detail[0]?.msg) {
              errorMessage = errorData.detail[0].msg;
            }
          }
        } catch {
          // If JSON parse fails, use fallback status text
        }
        throw new Error(errorMessage);
      }

      const data: PredictionResponse = await response.json();
      return data;
    } catch (err: unknown) {
      if (err instanceof Error) {
        // Enhance connection error message
        if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
          throw new Error(
            'Unable to reach the prediction service. Please ensure the backend server is active at ' +
              this.baseUrl
          );
        }
        throw err;
      }
      throw new Error('An unexpected error occurred during prediction.');
    }
  }

  /**
   * Sends a validated property prediction request to the V2 FastAPI endpoint.
   * Backend performs all feature engineering (Haversine distances, city grouping, etc.)
   */
  async predictV2(request: PredictionRequestV2): Promise<PredictionResponseV2> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v2/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        let errorMessage = `Server error (Status: ${response.status})`;
        try {
          const errorData = await response.json();
          if (errorData.detail) {
            if (typeof errorData.detail === 'string') {
              errorMessage = errorData.detail;
            } else if (Array.isArray(errorData.detail) && errorData.detail[0]?.msg) {
              errorMessage = errorData.detail[0].msg;
            }
          }
        } catch {
          // If JSON parse fails, use fallback status text
        }
        throw new Error(errorMessage);
      }

      const data: PredictionResponseV2 = await response.json();
      return data;
    } catch (err: unknown) {
      if (err instanceof Error) {
        if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
          throw new Error(
            'Unable to reach the V2 prediction service. Please ensure the backend server is active at ' +
              this.baseUrl
          );
        }
        throw err;
      }
      throw new Error('An unexpected error occurred during V2 prediction.');
    }
  }

  /**
   * Checks the health and readiness status of the backend ML service.
   */

  async checkHealth(): Promise<HealthResponse> {
    const response = await fetch(`${this.baseUrl}/health`, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Health check failed with status: ${response.status}`);
    }

    return response.json();
  }
}

export const predictionClient = new PredictionClient(API_BASE_URL);

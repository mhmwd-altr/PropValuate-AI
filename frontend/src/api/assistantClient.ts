import {
  AssistantChatRequest,
  AssistantChatResponse,
  AssistantResetResponse,
  AssistantHealthResponse,
} from '../types/assistant';

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
).replace(/\/+$/, '');

class AssistantClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  /**
   * Sends a chat message to the Language AI Assistant endpoint.
   */
  async sendMessage(message: string, sessionId?: string | null): Promise<AssistantChatResponse> {
    const payload: AssistantChatRequest = {
      message: message.trim(),
      session_id: sessionId || null,
    };

    try {
      const response = await fetch(`${this.baseUrl}/api/v2/assistant`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `Assistant API returned error HTTP ${response.status}`
        );
      }

      return await response.json();
    } catch (err: any) {
      console.error('[AssistantClient Error] sendMessage failed:', err);
      throw err;
    }
  }

  /**
   * Resets the active session and slot state on the backend.
   */
  async resetSession(sessionId: string): Promise<AssistantResetResponse> {
    try {
      const response = await fetch(
        `${this.baseUrl}/api/v2/assistant/reset?session_id=${encodeURIComponent(sessionId)}`,
        {
          method: 'POST',
          headers: {
            Accept: 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to reset session (HTTP ${response.status})`);
      }

      return await response.json();
    } catch (err: any) {
      console.error('[AssistantClient Error] resetSession failed:', err);
      throw err;
    }
  }

  /**
   * Checks the readiness and health of the Language AI service.
   */
  async getHealth(): Promise<AssistantHealthResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v2/assistant/health`, {
        method: 'GET',
        headers: {
          Accept: 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Health check failed (HTTP ${response.status})`);
      }

      return await response.json();
    } catch (err: any) {
      console.error('[AssistantClient Error] getHealth failed:', err);
      throw err;
    }
  }
}

export const assistantClient = new AssistantClient(API_BASE_URL);

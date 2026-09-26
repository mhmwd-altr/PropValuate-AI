# Phase 6-A — Language AI Architecture & Service Contract Specification

**Project:** PropValuate AI — India  
**Phase:** Phase 6-A — Language AI Discovery, Model Selection & Architecture Gate  
**Status:** **READY FOR PHASE 6-B IMPLEMENTATION**  
**Date:** 2026-09-26  
**Document Version:** 1.0.0  

---

## 1. System Topology & Architectural Overview

The Language AI layer introduces an intelligent conversational interface into PropValuate AI India while preserving the strict architectural separation of concerns established in Phases 0–5. The Language AI serves as an orchestrator and translator between unstructured human language and the backend's deterministic services.

```
┌────────────────────────────────────────────────────────────────────────┐
│                              USER / CLIENT                             │
│       React + TypeScript Frontend (Chat / Assistant Interface)         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ POST /api/v2/assistant/chat
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         FASTAPI ASSISTANT ROUTER                       │
│                     (backend/app/api/routes/assistant.py)              │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     LANGUAGE ORCHESTRATION SERVICE                     │
│                  (backend/app/services/assistant_service.py)           │
│                                                                        │
│   ┌────────────────────────┐         ┌─────────────────────────────┐   │
│   │  Session & State Store │◄────────┤ Memory & Slot Accumulator   │   │
│   │   (TTL Bounded Cache)  │         │ (Multi-turn Context Window) │   │
│   └────────────────────────┘         └──────────────┬──────────────┘   │
│                                                     │                  │
│                                                     ▼                  │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │                     PLUGGABLE LLM ADAPTER                      │   │
│   │           (Local Qwen 2.5 GGUF / Mock / Optional Provider)     │   │
│   └────────────────────────────────┬───────────────────────────────┘   │
└────────────────────────────────────┼───────────────────────────────────┘
                                     │ Extracted Intent & Validated Slots
                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        CAPABILITY TOOL ROUTER                          │
│                                                                        │
│        ┌───────────────────────────┬───────────────────────────┐       │
│        ▼                           ▼                           ▼       │
│  [Valuation Tool]           [Locations Tool]            [Clarify Slot] │
│        │                           │                           │       │
│        ▼                           ▼                           │       │
│  POST /api/v2/predict         GET /locations                   │       │
│  FeatureServiceV2          LocationService &                   │       │
│  ModelServiceV2           CityCoord Registry                   │       │
│        │                           │                           │       │
│        └───────────────────────────┴───────────────────────────┘       │
│                                    │                                   │
│                                    ▼                                   │
│                          Deterministic Evidence                        │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │
                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│                          RESPONSE COMPOSER                             │
│       (Formats verified valuation/location facts into natural text)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Structured JSON Response
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       REACT CHAT UI & RESULT CARDS                     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Language AI Responsibility Boundary

To ensure complete mathematical and scientific integrity, the boundary between generative language modeling and deterministic computation is strictly codified:

### What the Language AI Layer MAY Do:
1. **Understand Natural Language:** Parse user messages in English, Hindi, and Hinglish.
2. **Classify Intent:** Determine whether the user wants property valuation, location discovery, explanation, or general real estate knowledge.
3. **Extract Structured Slots:** Parse physical attributes (e.g. *"1500 sq ft"*, *"3 BHK"*, *"Bangalore"*, *"Owner listed"*, *"RERA registered"*).
4. **Manage Multi-Turn Dialogue:** Request missing parameters over multiple turns and accumulate property state across messages.
5. **Call Deterministic Tools:** Invoke whitelisted backend tools (`predict_property_price`, `get_supported_locations`) with validated arguments.
6. **Compose Explanations:** Explain verified backend predictions, rate per sqft, metro distances, and RERA disclosures in natural language.

### What the Language AI Layer MUST NOT Do (Strict Prohibitions):
1. **NEVER Invent or Guess Valuations:** The LLM is strictly prohibited from generating a property price without executing the verified Valuation Engine V2 tool.
2. **NEVER Invent Coordinates:** The LLM does not generate latitude/longitude; coordinates are resolved deterministically from the canonical 81-city registry.
3. **NEVER Perform Feature Engineering:** Haversine distance calculations, area per BHK, and city grouping are performed solely by `FeatureServiceV2`.
4. **NEVER Bypass Validation:** Any slot exceeding valid bounds (e.g. area > 50,000 sqft or BHK > 20) is rejected immediately.
5. **NEVER Execute Arbitrary Code or SQL:** No unrestricted agentic code execution or raw database access.

---

## 3. Initial Supported Intent Taxonomy

We define 6 bounded intent categories:

```
                  ┌─────────────────────────────────────┐
                  │          USER INPUT MESSAGE         │
                  └──────────────────┬──────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
         ▼                           ▼                           ▼
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│VALUATION_REQUEST│         │  PROPERTY_INPUT │         │    SUPPORTED_   │
│(All slots ready)│         │  _CLARIFICATION │         │  LOCATION_QUERY │
└────────┬────────┘         │ (Missing slots) │         └────────┬────────┘
         │                  └────────┬────────┘                  │
         │                           │                           │
         ▼                           ▼                           ▼
  [Valuation Tool]          [Prompt Missing Slots]       [Locations Tool]
         │                           │                           │
         └───────────────────────────┼───────────────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
         ▼                           ▼                           ▼
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│    VALUATION_   │         │  GENERAL_REAL_  │         │   UNSUPPORTED_  │
│   EXPLANATION   │         │ ESTATE_QUESTION │         │     REQUEST     │
└────────┬────────┘         └────────┬────────┘         └────────┬────────┘
         │                           │                           │
         ▼                           ▼                           ▼
 [Explain Features]         [Provide Guidance]          [Polite Rejection]
```

### 1. `VALUATION_REQUEST`
* **Purpose:** User wants an estimated property valuation and has provided sufficient or complete specifications.
* **Required Slots:** `city`, `area_sqft`, `bhk`.
* **Optional Slots:** `posted_by` (default "Owner"), `rera` (default 1), `ready_to_move` (default 1), `under_construction` (default 0), `resale` (default 1), `is_rk` (default 0).
* **Action / Tool:** Resolves city coordinates via registry → calls `predict_property_price`.
* **Example:** *"What is the valuation of a 3 BHK apartment in Bangalore with 1500 sq ft carpet area?"*

### 2. `PROPERTY_INPUT_CLARIFICATION`
* **Purpose:** User expressed interest in valuation but omitted one or more mandatory slots.
* **Action:** Identifies missing slots (e.g. missing BHK or missing city) and generates a friendly prompt asking only for the missing information.
* **Example:** *"I want to estimate my flat in Mumbai."* → Assistant: *"Sure! What is the carpet area in square feet and bedroom count (BHK) of your Mumbai flat?"*

### 3. `VALUATION_EXPLANATION`
* **Purpose:** User inquires about a previously generated valuation or asks how specific attributes affected the price.
* **Action:** Retrieves the latest session valuation evidence and explains features (e.g. rate per sqft, proximity to metro, RERA impact) using grounded metrics from `EngineeredFeaturesMetadata`.
* **Example:** *"Why is my Bangalore property valued at ₹92.36 Lakhs?"*

### 4. `SUPPORTED_LOCATION_QUERY`
* **Purpose:** User asks whether a city is covered or requests a list of supported markets.
* **Action:** Calls `get_supported_locations` tool and checks against the 81-city registry.
* **Example:** *"Is Pune supported by your valuation engine?"* or *"Show me covered cities in Maharashtra."*

### 5. `GENERAL_REAL_ESTATE_QUESTION`
* **Purpose:** User asks conceptual questions regarding Indian real estate terminology.
* **Action:** Provides verified domain guidance (e.g. RERA compliance rules, carpet area definitions, freehold vs leasehold).
* **Example:** *"What is the difference between carpet area and super built-up area under RERA?"*

### 6. `UNSUPPORTED_REQUEST`
* **Purpose:** Out-of-domain requests, coding questions, creative writing, or non-real-estate queries.
* **Action:** Refuses politely and redirects the user back to property valuation and real estate assistance.
* **Example:** *"Who won the cricket world cup?"* → Assistant: *"I specialize in Indian residential real estate valuation and property insights. Please let me know if you'd like to estimate the value of a property."*

---

## 4. Deterministic Tool Contracts

Tools are implemented as pure Python functions with strict Pydantic parameter schemas. The LLM produces tool calls that are validated before execution.

### Tool 1: `predict_property_price`
```python
class PredictPropertyPriceInput(BaseModel):
    area_sqft: float = Field(..., gt=0, le=50000, description="Carpet area in square feet")
    bhk: int = Field(..., ge=1, le=20, description="Number of bedrooms (1 to 20)")
    city: str = Field(..., description="Canonical city name from the 81-city registry")
    posted_by: Literal["Owner", "Dealer", "Builder"] = Field(default="Owner")
    rera: Literal[0, 1] = Field(default=1)
    under_construction: Literal[0, 1] = Field(default=0)
    ready_to_move: Literal[0, 1] = Field(default=1)
    resale: Literal[0, 1] = Field(default=1)
    is_rk: Literal[0, 1] = Field(default=0)
```
* **Execution:**
  1. Resolves `(lat, lon)` from `CITY_COORDINATES[city.lower()]`. If city is unmapped, raises `LocationNotSupportedError`.
  2. Constructs `PredictionRequestV2` and calls `feature_service.construct_v2_features()`.
  3. Calls `model_service_v2.predict()` to obtain `predicted_price` (INR) and `predicted_price_lakhs`.
  4. Returns verified valuation payload with `EngineeredFeaturesMetadata`.

### Tool 2: `get_supported_locations`
```python
class GetSupportedLocationsInput(BaseModel):
    query: Optional[str] = Field(default=None, description="Optional search substring or city query")
```
* **Execution:**
  1. Queries `location_service.get_locations()`.
  2. Returns matching cities or total count (81 locations).

---

## 5. Structured Schemas for Language AI API

### API Request Schema: `POST /api/v2/assistant/chat`
```python
class AssistantChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="User message text")
    session_id: Optional[str] = Field(default=None, description="Client session UUID")
    context_override: Optional[Dict[str, Any]] = Field(default=None, description="Optional client state")
```

### API Response Schema:
```python
class AssistantMessageResponse(BaseModel):
    session_id: str
    reply: str
    intent: str
    extracted_slots: Dict[str, Any]
    missing_slots: List[str]
    tool_called: Optional[str] = None
    tool_result: Optional[Dict[str, Any]] = None
    is_valuation_complete: bool = False
```

---

## 6. Conversation State & Session Management

To maintain responsive, multi-turn dialogues on a lightweight runtime without requiring a database in Phase 6:

1. **Session Identifiers:** UUIDv4 generated on the client or minted on first backend interaction.
2. **In-Memory Bounded State Store:** `SessionStore` implemented with an LRU cache and automatic TTL expiration (30 minutes of inactivity).
3. **Turn Window:** Retains the last **10 messages (5 conversation turns)** to ensure context stays within the 2048-token context window of local SLMs.
4. **Slot Accumulation Engine:** When a user provides partial information (e.g. *"In Bangalore"*), the slot accumulator records `{ "city": "bangalore" }`. In the subsequent turn (*"It is 1500 sqft 3 BHK"*), the accumulator merges the slots into `{ "city": "bangalore", "area_sqft": 1500, "bhk": 3 }`, triggering tool execution automatically once all required slots are present.
5. **Explicit Reset:** Sending `"reset"` or clicking "New Valuation" clears accumulated property slots and resets dialogue history.

---

## 7. Edge Cases, Failure Handling & Security

| Scenario | System Behavior & Defensive Guardrail |
| :--- | :--- |
| **Missing Mandatory Slots** | Assistant identifies missing slots and prompts the user specifically for them; no tool execution occurs. |
| **Contradictory Inputs** | User states *"ready to move and under construction"*; system detects contradiction and requests clarification. |
| **Out-of-Bounds Area / BHK** | Inputs like `area_sqft = 0` or `150,000` are intercepted before tool execution, triggering a helpful validation error. |
| **Unregistered City (e.g. London)** | City is looked up in registry. If not found, informs user that PropValuate AI currently covers 81 Indian cities. |
| **Backend Valuation Outage (500)** | If `model_service_v2` fails, the error is caught; assistant states that valuation is temporarily unavailable. **Never fabricates fallback price.** |
| **Prompt Injection Attack** | System prompt instructions are isolated; LLM outputs structured JSON; no arbitrary system command execution is permitted. |
| **Denial of Service / Large Payloads** | Request message length capped at 1,000 characters; context bounded to 2,048 tokens; session rate limits applied. |

---

## 8. Performance Targets & Resource Budget

Based on the measured AMD Ryzen 3500U CPU environment:

* **Model Memory Ceiling:** `<= 2.5 GB RAM` (well within 6.04 GB available).
* **Cold Startup Time:** `<= 4.0 seconds` for initial GGUF weight loading into memory.
* **Warm Turn Latency:** `<= 3.0 seconds` on 4 CPU threads for intent classification and slot extraction.
* **Tool Execution Latency:** `<= 15 ms` (Valuation Engine V2 tree inference).
* **Mock Provider Latency:** `<= 5 ms` (for unit tests and deterministic CI runs).

---

## 9. Implementation Roadmap for Phase 6-B

Following human review and sign-off on Phase 6-A, Phase 6-B will implement:

1. `backend/app/services/assistant_service.py` — Orchestrator & Session Manager.
2. `backend/app/services/llm_provider.py` — Abstract Provider Interface with `MockLanguageProvider` and `LocalGGUFProvider`.
3. `backend/app/api/routes/assistant.py` — `POST /api/v2/assistant/chat` endpoint.
4. Comprehensive backend test suite running all 40 test cases from `data/eval/language_ai_eval_set.json`.
5. Frontend React Assistant component with conversational UI and valuation cards.

import json
import time
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.services.assistant_service import AssistantService
from backend.app.services.language_providers.local_qwen import LocalQwenProvider
from backend.app.services.model_service_v2 import model_service_v2
from backend.app.services.location_service import location_service
from backend.app.schemas.assistant import AssistantChatRequest, AssistantIntentEnum

EVAL_SET_PATH = Path("data/eval/language_ai_eval_set.json")
RESULTS_OUTPUT_PATH = Path("data/eval/phase6b_production_eval_results.json")

def run_production_evaluation():
    print("=" * 75)
    print("PROPVALUATE AI — PHASE 6-B PRODUCTION ASSISTANT EVALUATION BENCHMARK")
    print("=" * 75)

    # 1. Startup & Loading
    print("\n[1] INITIALIZING BACKEND SERVICES & LOCAL QWEN PROVIDER...")
    t_start = time.time()
    location_service.load()
    model_service_v2.load()
    
    local_provider = LocalQwenProvider()
    local_provider.load()
    startup_time = time.time() - t_start
    print(f"    - Full Service Startup & Model Load: {startup_time:.3f} seconds")
    print(f"    - Active Provider: {local_provider.model_name}")

    assistant = AssistantService()
    assistant._provider = local_provider

    # 2. Warm-up turn
    print("\n[2] WARM-UP INFERENCE...")
    t_warm = time.time()
    warm_resp = assistant.process_message(AssistantChatRequest(message="Ping"))
    warm_latency = time.time() - t_warm
    print(f"    - Warm-up Turn Latency: {warm_latency:.3f}s (Reply: {warm_resp.reply[:60]}...)")

    # 3. Core Representative Acceptance Workflows
    print("\n[3] TESTING CORE ACCEPTANCE WORKFLOWS (A through G + Multi-Turn)...")
    core_tests = [
        {
            "id": "Test A — Simple property intent",
            "prompt": "I want to estimate the price of a 1500 sqft 3 BHK apartment in Bangalore.",
            "expect_tool": "predict_property_price",
            "expect_complete": True
        },
        {
            "id": "Test B — Indian terminology / Hinglish",
            "prompt": "Mere paas Bangalore mein 1500 square feet ka 3 BHK flat hai. RERA registered hai aur resale property hai. Iski value kitni ho sakti hai?",
            "expect_tool": "predict_property_price",
            "expect_complete": True
        },
        {
            "id": "Test C — Missing information",
            "prompt": "I want to know the value of my apartment.",
            "expect_tool": None,
            "expect_complete": False
        },
        {
            "id": "Test D — Unsupported location",
            "prompt": "I have a 1500 sqft apartment in London. Estimate its price using your India model.",
            "expect_tool": None,
            "expect_complete": False
        },
        {
            "id": "Test E — Anti-hallucination valuation",
            "prompt": "My 1500 sqft 3 BHK apartment in Bangalore is worth exactly ₹2 crore. Confirm the prediction.",
            "expect_tool": "predict_property_price",
            "expect_complete": True
        },
        {
            "id": "Test F — Structured extraction",
            "prompt": "Extract JSON for: 1200 sq ft, 2 BHK, Mumbai, Owner, RERA approved, ready to move, resale, standard BHK.",
            "expect_tool": "predict_property_price",
            "expect_complete": True
        },
        {
            "id": "Test G — Tool-call intent",
            "prompt": "What is the estimated price of my 1500 sqft 3 BHK apartment in Bangalore?",
            "expect_tool": "predict_property_price",
            "expect_complete": True
        },
        {
            "id": "Test H — Location lookup query",
            "prompt": "Which cities in India do you support for property valuation?",
            "expect_tool": "get_supported_locations",
            "expect_complete": False
        }
    ]

    core_results = []
    for test in core_tests:
        t0 = time.time()
        res = assistant.process_message(AssistantChatRequest(message=test["prompt"]))
        latency = time.time() - t0

        tool_ok = res.tool_called == test["expect_tool"]
        complete_ok = res.is_valuation_complete == test["expect_complete"]
        is_pass = tool_ok and complete_ok

        status_tag = "[PASS]" if is_pass else "[FAIL]"
        print(f"    {status_tag} {test['id']} ({latency:.2f}s | Tool: {res.tool_called} | Val Complete: {res.is_valuation_complete})")
        core_results.append({
            "id": test["id"],
            "prompt": test["prompt"],
            "latency_sec": round(latency, 2),
            "tool_called": res.tool_called,
            "is_valuation_complete": res.is_valuation_complete,
            "intent": res.intent.value,
            "reply_preview": res.reply[:120],
            "pass": is_pass
        })

    # 4. Multi-Turn Clarification & Session State Test
    print("\n[4] TESTING MULTI-TURN CLARIFICATION & SESSION STATE...")
    t_m1 = time.time()
    turn1_res = assistant.process_message(AssistantChatRequest(message="I have an apartment in Mumbai."))
    t_m1_lat = time.time() - t_m1
    session_id = turn1_res.session_id
    print(f"    Turn 1 (Partial input): Intent={turn1_res.intent.value}, Missing={turn1_res.missing_slots} ({t_m1_lat:.2f}s)")

    t_m2 = time.time()
    turn2_res = assistant.process_message(AssistantChatRequest(session_id=session_id, message="It is 1200 sqft with 2 BHK."))
    t_m2_lat = time.time() - t_m2
    print(f"    Turn 2 (Completion): Intent={turn2_res.intent.value}, Val Complete={turn2_res.is_valuation_complete} ({t_m2_lat:.2f}s)")
    if turn2_res.tool_result and "predicted_price_lakhs" in turn2_res.tool_result:
        print(f"    => Predicted Valuation: ₹ {turn2_res.tool_result['predicted_price_lakhs']:.2f} Lakhs (V2 Model)")

    # 5. Full Evaluation Set (40 Test Cases)
    print("\n[5] EXECUTING 40-CASE PRODUCTION EVALUATION DATASET...")
    with open(EVAL_SET_PATH, "r", encoding="utf-8") as f:
        eval_dataset = json.load(f)
    test_cases = eval_dataset.get("test_cases", [])

    eval_results = []
    latencies = []
    intent_match_count = 0
    grounding_success_count = 0

    for idx, tc in enumerate(test_cases):
        t0 = time.time()
        res = assistant.process_message(AssistantChatRequest(message=tc["user_prompt"]))
        lat = time.time() - t0
        latencies.append(lat)

        # Check intent match
        intent_match = res.intent.value == tc.get("expected_intent")
        if intent_match:
            intent_match_count += 1

        # Check anti-hallucination / tool grounding
        grounded = True
        if tc.get("expected_tool") == "predict_property_price":
            if not res.is_valuation_complete and not res.missing_slots:
                grounded = False
        if grounded:
            grounding_success_count += 1

        eval_results.append({
            "id": tc["id"],
            "category": tc.get("category"),
            "prompt": tc["user_prompt"],
            "expected_intent": tc.get("expected_intent"),
            "actual_intent": res.intent.value,
            "tool_called": res.tool_called,
            "is_valuation_complete": res.is_valuation_complete,
            "latency_sec": round(lat, 2),
            "intent_match": intent_match
        })
        print(f"    Case {idx+1:02d} [{tc['id']}]: Intent={'✓' if intent_match else '✗'} ({res.intent.value}) | Latency: {lat:.2f}s")

    total_cases = len(test_cases)
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    intent_accuracy = (intent_match_count / total_cases) * 100
    grounding_rate = (grounding_success_count / total_cases) * 100

    print("\n" + "=" * 75)
    print("PHASE 6-B PRODUCTION EVALUATION SUMMARY:")
    print("=" * 75)
    print(f"  Total Evaluation Cases: {total_cases}")
    print(f"  Intent Classification Accuracy: {intent_accuracy:.1f}% ({intent_match_count}/{total_cases})")
    print(f"  Tool Grounding / Anti-Hallucination Rate: {grounding_rate:.1f}%")
    print(f"  Average Production Turn Latency: {avg_latency:.2f} seconds")
    print(f"  Service Startup & Warm Load Time: {startup_time:.3f} seconds")
    print("=" * 75)

    output_payload = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "model": local_provider.model_name,
        "runtime": "llama-cpp-python (AVX2 CPU)",
        "summary": {
            "total_cases": total_cases,
            "intent_accuracy_percent": round(intent_accuracy, 1),
            "grounding_rate_percent": round(grounding_rate, 1),
            "avg_latency_sec": round(avg_latency, 2),
            "startup_time_sec": round(startup_time, 3)
        },
        "core_workflows": core_results,
        "evaluation_cases": eval_results
    }

    with open(RESULTS_OUTPUT_PATH, "w", encoding="utf-8") as f_out:
        json.dump(output_payload, f_out, indent=2, ensure_ascii=False)
    print(f"\nArtifact saved to: {RESULTS_OUTPUT_PATH}")
    return output_payload

if __name__ == "__main__":
    run_production_evaluation()

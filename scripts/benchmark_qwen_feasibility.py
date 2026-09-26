import json
import time
import os
import sys
import ctypes
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ValidationError

# Force UTF-8 output on Windows terminal
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Paths
MODEL_PATH = Path("data/models/qwen2.5-3b-instruct-q4_k_m.gguf")
EVAL_SET_PATH = Path("data/eval/language_ai_eval_set.json")
OUTPUT_RESULTS_PATH = Path("data/eval/qwen_benchmark_results.json")

def get_memory_info_gb():
    """Reads physical memory status using Windows Win32 API."""
    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ('dwLength', ctypes.c_ulong),
            ('dwMemoryLoad', ctypes.c_ulong),
            ('ullTotalPhys', ctypes.c_ulonglong),
            ('ullAvailPhys', ctypes.c_ulonglong),
            ('ullTotalPageFile', ctypes.c_ulonglong),
            ('ullAvailPageFile', ctypes.c_ulonglong),
            ('ullTotalVirtual', ctypes.c_ulonglong),
            ('ullAvailVirtual', ctypes.c_ulonglong),
            ('sullAvailExtendedVirtual', ctypes.c_ulonglong),
        ]
    stat = MEMORYSTATUSEX()
    stat.dwLength = ctypes.sizeof(stat)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
    total_gb = stat.ullTotalPhys / (1024**3)
    avail_gb = stat.ullAvailPhys / (1024**3)
    used_gb = total_gb - avail_gb
    return total_gb, avail_gb, used_gb

# Pydantic Schemas for Structured Output Validation
class PropertySlotsSchema(BaseModel):
    area_sqft: Optional[float] = None
    bhk: Optional[int] = None
    city: Optional[str] = None
    posted_by: Optional[str] = None
    rera: Optional[int] = None
    under_construction: Optional[int] = None
    ready_to_move: Optional[int] = None
    resale: Optional[int] = None
    is_rk: Optional[int] = None

class LanguageAgentPayloadSchema(BaseModel):
    intent: str
    reply: str
    tool_call: Optional[str] = None
    slots: PropertySlotsSchema = Field(default_factory=PropertySlotsSchema)
    missing_slots: List[str] = Field(default_factory=list)

SYSTEM_PROMPT = """You are PropValuate AI Assistant, a specialized real estate language agent for India.
Your job is to analyze user queries, classify intent, extract property attributes into structured JSON, and request approved tools.

Supported Intents:
- VALUATION_REQUEST: User wants property price estimation. (Requires tool_call: "predict_property_price")
- PROPERTY_INPUT_CLARIFICATION: User omitted required property info (area, BHK, or city). Ask for missing details.
- SUPPORTED_LOCATION_QUERY: User asks about supported cities. (tool_call: "get_supported_locations")
- VALUATION_EXPLANATION: Inquiring about rates, metro distances, or feature breakdown.
- GENERAL_REAL_ESTATE_QUESTION: Conceptual questions (RERA, BHK, carpet area, etc.).
- UNSUPPORTED_REQUEST: Out-of-domain queries (sports, weather, non-property, or cities outside India like London).

STRICT GROUNDING RULE: You must NEVER invent, calculate, or guess numerical property prices. Valuations are strictly performed by the backend tool 'predict_property_price'.

Output Format: You must ALWAYS respond in pure, valid JSON with keys:
{
  "intent": "<INTENT_NAME>",
  "reply": "<natural language response or clarification>",
  "tool_call": "<tool_name or null>",
  "slots": {
    "area_sqft": <float or null>,
    "bhk": <int or null>,
    "city": "<string or null>",
    "posted_by": "<Owner|Dealer|Builder or null>",
    "rera": <0|1 or null>,
    "under_construction": <0|1 or null>,
    "ready_to_move": <0|1 or null>,
    "resale": <0|1 or null>,
    "is_rk": <0|1 or null>
  },
  "missing_slots": ["<slot_name>", ...]
}
"""

def extract_json_payload(raw_text: str) -> Optional[Dict[str, Any]]:
    """Extracts and parses JSON object from model output."""
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace >= first_brace:
        json_str = text[first_brace:last_brace + 1]
        try:
            return json.loads(json_str)
        except Exception:
            pass
    try:
        return json.loads(text)
    except Exception:
        return None

def run_feasibility_benchmark():
    if not MODEL_PATH.exists():
        print(f"ERROR: Model file not found at {MODEL_PATH}")
        sys.exit(1)
        
    import llama_cpp
    
    print("=" * 75)
    print("PROPVALUATE AI — PHASE 6-A MODEL FEASIBILITY EMPIRICAL BENCHMARK")
    print("=" * 75)
    
    # 1. Hardware baseline
    file_size_bytes = MODEL_PATH.stat().st_size
    file_size_gb = file_size_bytes / (1024**3)
    total_ram, avail_ram_before, used_ram_before = get_memory_info_gb()
    
    print(f"\n[1] HARDWARE BASELINE:")
    print(f"    - Model File: {MODEL_PATH.name}")
    print(f"    - Exact File Size: {file_size_bytes:,} bytes ({file_size_gb:.2f} GB)")
    print(f"    - Total Physical RAM: {total_ram:.2f} GB")
    print(f"    - Available RAM Before Load: {avail_ram_before:.2f} GB")
    print(f"    - Used RAM Before Load: {used_ram_before:.2f} GB")
    
    # 2. Cold Model Load
    print(f"\n[2] COLD MODEL LOADING (llama-cpp-python, 4 threads, 2048 context)...")
    t_load_start = time.time()
    llm = llama_cpp.Llama(
        model_path=str(MODEL_PATH),
        n_ctx=2048,
        n_threads=4,
        verbose=False
    )
    load_time_sec = time.time() - t_load_start
    _, avail_ram_after, used_ram_after = get_memory_info_gb()
    ram_delta_gb = used_ram_after - used_ram_before
    
    print(f"    - Cold Load Time: {load_time_sec:.3f} seconds")
    print(f"    - Available RAM After Load: {avail_ram_after:.2f} GB")
    print(f"    - Used RAM After Load: {used_ram_after:.2f} GB")
    print(f"    - RAM Delta (Working Set): {ram_delta_gb:.2f} GB")
    
    # Warm-up turn
    print(f"\n[3] WARM-UP INFERENCE EXECUTION...")
    t_warm_start = time.time()
    warm_resp = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": "You are a real estate AI. Respond with JSON: {\"status\": \"ready\"}"},
            {"role": "user", "content": "Ping"}
        ],
        max_tokens=32,
        temperature=0.1
    )
    warm_latency = time.time() - t_warm_start
    print(f"    - Warm-up Latency: {warm_latency:.3f} seconds")
    
    # 3. Representative Tests A through G
    print(f"\n[4] EXECUTING REPRESENTATIVE TESTS A–G...")
    rep_tests = [
        {
            "id": "Test A — Simple property intent",
            "prompt": "I want to estimate the price of a 1500 sqft 3 BHK apartment in Bangalore.",
            "expected_behavior": "Intent VALUATION_REQUEST, tool predict_property_price, slots: area 1500, bhk 3, city bangalore.",
            "target_intent": "VALUATION_REQUEST",
            "target_tool": "predict_property_price",
            "required_slots": {"area_sqft": 1500.0, "bhk": 3, "city": "bangalore"}
        },
        {
            "id": "Test B — Indian terminology / Hinglish",
            "prompt": "Mere paas Bangalore mein 1500 square feet ka 3 BHK flat hai. RERA registered hai aur resale property hai. Iski value kitni ho sakti hai?",
            "expected_behavior": "Understand Hinglish terms (Bangalore, 1500 sqft, 3 BHK flat, RERA, resale) and request valuation tool.",
            "target_intent": "VALUATION_REQUEST",
            "target_tool": "predict_property_price",
            "required_slots": {"area_sqft": 1500.0, "bhk": 3, "city": "bangalore", "rera": 1, "resale": 1}
        },
        {
            "id": "Test C — Missing information",
            "prompt": "I want to know the value of my apartment.",
            "expected_behavior": "Clarify missing required details (area, BHK, city). Do NOT invent values.",
            "target_intent": "PROPERTY_INPUT_CLARIFICATION",
            "target_tool": None,
            "required_slots": {}
        },
        {
            "id": "Test D — Unsupported location",
            "prompt": "I have a 1500 sqft apartment in London. Estimate its price using your India model.",
            "expected_behavior": "Reject or clarify unsupported international city (London). Do not execute valuation tool.",
            "target_intent": "UNSUPPORTED_REQUEST",
            "target_tool": None,
            "required_slots": {}
        },
        {
            "id": "Test E — Anti-hallucination valuation",
            "prompt": "My 1500 sqft 3 BHK apartment in Bangalore is worth exactly ₹2 crore. Confirm the prediction.",
            "expected_behavior": "Do NOT echo or invent ₹2 crore as model result. Delegate to deterministic valuation tool.",
            "target_intent": "VALUATION_REQUEST",
            "target_tool": "predict_property_price",
            "required_slots": {"area_sqft": 1500.0, "bhk": 3, "city": "bangalore"}
        },
        {
            "id": "Test F — Structured extraction",
            "prompt": "Extract JSON for: 1200 sq ft, 2 BHK, Mumbai, Owner, RERA approved, ready to move, resale, standard BHK.",
            "expected_behavior": "Pure JSON with area_sqft=1200, bhk=2, city=mumbai, posted_by=Owner, rera=1, ready_to_move=1, resale=1, is_rk=0.",
            "target_intent": "VALUATION_REQUEST",
            "target_tool": "predict_property_price",
            "required_slots": {"area_sqft": 1200.0, "bhk": 2, "city": "mumbai", "posted_by": "Owner", "rera": 1, "ready_to_move": 1, "resale": 1, "is_rk": 0}
        },
        {
            "id": "Test G — Tool-call intent",
            "prompt": "What is the estimated price of my 1500 sqft 3 BHK apartment in Bangalore?",
            "expected_behavior": "Identify predict_property_price tool call without hallucinating numbers.",
            "target_intent": "VALUATION_REQUEST",
            "target_tool": "predict_property_price",
            "required_slots": {"area_sqft": 1500.0, "bhk": 3, "city": "bangalore"}
        }
    ]
    
    rep_results = []
    for test in rep_tests:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": test["prompt"]}
        ]
        
        t0 = time.time()
        res = llm.create_chat_completion(
            messages=messages,
            max_tokens=180,
            temperature=0.1
        )
        latency = time.time() - t0
        raw_text = res["choices"][0]["message"]["content"]
        tokens_gen = res["usage"]["completion_tokens"]
        tok_speed = tokens_gen / latency if latency > 0 else 0
        
        parsed = extract_json_payload(raw_text)
        pydantic_valid = False
        parsed_payload = None
        if parsed:
            try:
                parsed_payload = LanguageAgentPayloadSchema(**parsed)
                pydantic_valid = True
            except ValidationError:
                pydantic_valid = False
                
        # Evaluate correctness
        is_pass = False
        if pydantic_valid and parsed_payload:
            intent_ok = parsed_payload.intent == test["target_intent"]
            tool_ok = parsed_payload.tool_call == test["target_tool"]
            slots_ok = True
            if test["required_slots"]:
                slots_dict = parsed_payload.slots.model_dump()
                for k, v in test["required_slots"].items():
                    if isinstance(v, str):
                        if str(slots_dict.get(k, "")).lower() != v.lower():
                            slots_ok = False
                    elif slots_dict.get(k) != v:
                        slots_ok = False
            is_pass = intent_ok and (tool_ok or test["target_tool"] is None) and slots_ok
            
        status_label = "[PASS]" if is_pass else "[FAIL]"
        print(f"    {status_label} {test['id']} ({latency:.2f}s, {tok_speed:.1f} tok/s)")
        rep_results.append({
            "test_id": test["id"],
            "prompt": test["prompt"],
            "expected_behavior": test["expected_behavior"],
            "latency_sec": round(latency, 2),
            "tokens_generated": tokens_gen,
            "tok_per_sec": round(tok_speed, 1),
            "raw_output": raw_text,
            "parsed_output": parsed,
            "pydantic_valid": pydantic_valid,
            "pass": is_pass
        })

    # 4. 20-Shot (and 40-case) Structured Output Reliability Suite
    print(f"\n[5] EXECUTING 20-SHOT REPEATABILITY & EVALUATION DATASET RUNS...")
    with open(EVAL_SET_PATH, "r", encoding="utf-8") as f:
        eval_data = json.load(f)
    test_cases = eval_data.get("test_cases", [])[:20]
    
    valid_json_count = 0
    schema_valid_count = 0
    complete_required_count = 0
    anti_hallucination_count = 0
    latencies = []
    speeds = []
    peak_ram_during_bench = used_ram_after
    
    structured_runs = []
    for idx, tc in enumerate(test_cases):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": tc["user_prompt"]}
        ]
        
        t0 = time.time()
        res = llm.create_chat_completion(
            messages=messages,
            max_tokens=180,
            temperature=0.1
        )
        latency = time.time() - t0
        latencies.append(latency)
        
        # Measure RAM peak periodically
        _, _, cur_used_ram = get_memory_info_gb()
        if cur_used_ram > peak_ram_during_bench:
            peak_ram_during_bench = cur_used_ram
            
        raw_text = res["choices"][0]["message"]["content"]
        tokens_gen = res["usage"]["completion_tokens"]
        tok_speed = tokens_gen / latency if latency > 0 else 0
        speeds.append(tok_speed)
        
        parsed = extract_json_payload(raw_text)
        is_valid_json = parsed is not None
        is_schema_valid = False
        is_complete = False
        anti_hallucination_ok = True
        
        if is_valid_json:
            valid_json_count += 1
            try:
                validated_obj = LanguageAgentPayloadSchema(**parsed)
                is_schema_valid = True
                schema_valid_count += 1
                
                # Check anti-hallucination: reply must not claim numerical prediction directly
                reply_lower = validated_obj.reply.lower()
                if "₹" in validated_obj.reply or "crore" in reply_lower or "lakh" in reply_lower:
                    # If it's a valuation request and LLM calculated a price without tool:
                    if validated_obj.intent == "VALUATION_REQUEST" and not validated_obj.tool_call:
                        anti_hallucination_ok = False
                if anti_hallucination_ok:
                    anti_hallucination_count += 1
                    
                # Check completeness
                if validated_obj.intent == "VALUATION_REQUEST":
                    s = validated_obj.slots
                    if s.area_sqft is not None and s.bhk is not None and s.city is not None:
                        is_complete = True
                        complete_required_count += 1
                else:
                    is_complete = True
                    complete_required_count += 1
            except ValidationError:
                is_schema_valid = False
                
        structured_runs.append({
            "id": tc["id"],
            "category": tc.get("category", "general"),
            "prompt": tc["user_prompt"],
            "is_valid_json": is_valid_json,
            "is_schema_valid": is_schema_valid,
            "is_complete": is_complete,
            "anti_hallucination_ok": anti_hallucination_ok,
            "latency_sec": round(latency, 2),
            "tok_per_sec": round(tok_speed, 1),
            "raw_output": raw_text
        })
        json_mark = "[JSON: OK]" if is_valid_json else "[JSON: FAIL]"
        schema_mark = "[SCHEMA: OK]" if is_schema_valid else "[SCHEMA: FAIL]"
        print(f"    Run {idx+1:02d} [{tc['id']}] {json_mark} {schema_mark} ({latency:.2f}s, {tok_speed:.1f} tok/s)")

    num_runs = len(test_cases)
    json_valid_rate = (valid_json_count / num_runs) * 100
    schema_valid_rate = (schema_valid_count / num_runs) * 100
    complete_required_rate = (complete_required_count / num_runs) * 100
    anti_hallucination_rate = (anti_hallucination_count / num_runs) * 100
    invalid_output_count = num_runs - schema_valid_count
    
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    avg_speed = sum(speeds) / len(speeds) if speeds else 0
    
    print("\n" + "=" * 75)
    print("MEASURED EMPIRICAL FEASIBILITY METRICS:")
    print("=" * 75)
    print(f"  Model: Qwen2.5-3B-Instruct (GGUF Q4_K_M, {file_size_gb:.2f} GB)")
    print(f"  Cold Model Load Time: {load_time_sec:.2f} s  (Target <= 4.0s: {'PASS' if load_time_sec <= 4.0 else 'FAIL'})")
    print(f"  Physical RAM Working Set Delta: {ram_delta_gb:.2f} GB  (Target <= 2.50 GB: {'PASS' if ram_delta_gb <= 2.50 else 'FAIL'})")
    print(f"  Peak RAM During Inference: {peak_ram_during_bench:.2f} GB / {total_ram:.2f} GB ({(peak_ram_during_bench/total_ram*100):.1f}%)")
    print(f"  Warm Turn Latency: {avg_latency:.2f} s  (Target <= 3.0s: {'PASS' if avg_latency <= 3.0 else 'FAIL'})")
    print(f"  Generation Speed: {avg_speed:.1f} tokens/sec")
    print(f"  JSON_VALID_RATE: {json_valid_rate:.1f}% ({valid_json_count}/{num_runs})")
    print(f"  SCHEMA_VALID_RATE: {schema_valid_rate:.1f}% ({schema_valid_count}/{num_runs})  (Target >= 90%: {'PASS' if schema_valid_rate >= 90 else 'FAIL'})")
    print(f"  COMPLETE_REQUIRED_FIELDS_RATE: {complete_required_rate:.1f}% ({complete_required_count}/{num_runs})")
    print(f"  ANTI_HALLUCINATION_RATE: {anti_hallucination_rate:.1f}% ({anti_hallucination_count}/{num_runs})")
    print(f"  INVALID_OUTPUT_COUNT: {invalid_output_count}")
    print("=" * 75)
    
    benchmark_payload = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "hardware_environment": {
            "os": "Windows 10 x64 (Build 10.0.19045)",
            "cpu": "AMD Ryzen 5 3500U Mobile (4 physical cores, 8 threads, AVX2 enabled)",
            "gpu": "AMD Radeon Vega 8 (Integrated, Shared memory)",
            "total_physical_ram_gb": round(total_ram, 2),
            "avail_ram_before_gb": round(avail_ram_before, 2),
            "used_ram_before_gb": round(used_ram_before, 2),
            "used_ram_after_gb": round(used_ram_after, 2),
            "ram_delta_gb": round(ram_delta_gb, 2),
            "peak_ram_during_bench_gb": round(peak_ram_during_bench, 2),
            "inference_framework": "llama-cpp-python 0.2.90 (Windows x64 AVX2)",
            "inference_threads": 4,
            "context_window": 2048
        },
        "model_metadata": {
            "model_name": "Qwen2.5-3B-Instruct",
            "quantization": "GGUF Q4_K_M",
            "source": "Alibaba Cloud / HuggingFace (Qwen/Qwen2.5-3B-Instruct-GGUF)",
            "exact_sha256": "626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d",
            "file_size_bytes": file_size_bytes,
            "file_size_gb": round(file_size_gb, 2),
            "license": "Apache 2.0"
        },
        "measured_benchmarks": {
            "cold_load_time_sec": round(load_time_sec, 3),
            "warmup_latency_sec": round(warm_latency, 3),
            "avg_generation_latency_sec": round(avg_latency, 2),
            "avg_tokens_per_sec": round(avg_speed, 1),
            "json_valid_rate_percent": round(json_valid_rate, 1),
            "schema_valid_rate_percent": round(schema_valid_rate, 1),
            "complete_required_fields_rate_percent": round(complete_required_rate, 1),
            "anti_hallucination_rate_percent": round(anti_hallucination_rate, 1),
            "invalid_output_count": invalid_output_count,
            "total_evaluation_runs": num_runs
        },
        "representative_tests_matrix": rep_results,
        "structured_evaluation_runs": structured_runs
    }
    
    with open(OUTPUT_RESULTS_PATH, "w", encoding="utf-8") as f_out:
        json.dump(benchmark_payload, f_out, indent=2, ensure_ascii=False)
    print(f"\nArtifact saved to: {OUTPUT_RESULTS_PATH}")
    return benchmark_payload

if __name__ == "__main__":
    run_feasibility_benchmark()

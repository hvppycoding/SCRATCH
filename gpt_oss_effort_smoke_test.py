#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gpt_oss_effort_smoke_test.py

Mini smoke test to infer the default reasoning_effort for your GPT-OSS endpoint
and verify Low/Medium/High switches affect latency and tokens.

USAGE
-----
1) Set environment variables:
   export ENDPOINT_URL="https://<your-endpoint>"
   export API_KEY="sk-..."
2) (Optional) Choose model id via CLI: --model gpt-oss-20b
3) Run:
   python gpt_oss_effort_smoke_test.py --repeats 2

This will:
- Send a compact set of short-but-not-trivial prompts.
- Call the endpoint with four variants per prompt:
    A) effort unspecified  (to detect actual DEFAULT)
    B) effort = "medium"
    C) effort = "low"
    D) effort = "high"
- Log per-call latency, tokens, and short text preview.
- Save results to runs.jsonl and summary.csv.
- Print a quick table showing means by effort (latency / tokens).

Notes
-----
- The script assumes an OpenAI-compatible chat completions API that returns:
    { choices: [{ message: { content: str }}],
      usage: { prompt_tokens, completion_tokens, reasoning_tokens? } }
- If your API names differ, adjust parse_usage().
- The script retries transient HTTP errors with backoff.
"""

import argparse
import json
import os
import random
import sys
import time
from datetime import datetime
from typing import Any, Dict, Optional

import requests

# ---------- Configurable defaults ----------

DEFAULT_MODEL = "gpt-oss-20b"
DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_TOKENS = 512
DEFAULT_SEED = 42
DEFAULT_TIMEOUT = 60
DEFAULT_REPEATS = 2

PROMPTS = [
    {
        "id": "math_boxes",
        "text": (
            "3개의 상자에 각각 4, 7, 9개의 사탕이 있다. "
            "상자 2에서 5개를 꺼내 상자 1에 넣고, 상자 3에서 2개를 꺼내 상자 2에 넣으면, "
            "각 상자에는 몇 개씩 남는가? 최종 결과만 한국어로 말해줘."
        ),
    },
    {
        "id": "logic_race",
        "text": (
            "철수, 영희, 민수는 달리기 시합을 했다. 철수는 영희보다 빠르고, "
            "영희는 민수보다 느리다. 누가 1등인가? 한 단어로만 답해."
        ),
    },
    {
        "id": "date_calc",
        "text": (
            "오늘이 2025년 8월 11일이라면, 45일 후는 무슨 요일인가?"
            " 한국 시간대를 기준으로, 요일만 한국어로 답해."
        ),
    },
    {
        "id": "weight_sum",
        "text": (
            "사과는 500g, 배는 700g이다. 사과 3개와 배 2개의 총 무게는 몇 kg인가? "
            "소수점 둘째 자리까지 kg 단위로만 답해."
        ),
    },
    {
        "id": "sequence",
        "text": "수열 2, 4, 8, 16, ? 다음 숫자는? 숫자만."
    },
]

EFFORT_LEVELS = [None, "medium", "low", "high"]  # None = unspecified (to detect actual default)

# ---------- Helpers ----------

def env(key: str, default: Optional[str] = None) -> str:
    val = os.getenv(key, default)
    if val is None:
        print(f"[ERROR] Missing environment variable: {key}", file=sys.stderr)
        sys.exit(1)
    return val

def parse_usage(obj: Dict[str, Any]) -> Dict[str, Optional[int]]:
    usage = obj.get("usage", {}) or {}
    return {
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "reasoning_tokens": usage.get("reasoning_tokens"),  # optional
        "total_tokens": usage.get("total_tokens"),
    }

def short(s: Optional[str], n: int = 80) -> str:
    if not s:
        return ""
    s = s.replace("\n", " ").strip()
    return s[:n] + ("…" if len(s) > n else "")

def post_with_retries(url: str, headers: Dict[str, str], payload: Dict[str, Any], timeout: int) -> requests.Response:
    backoffs = [0.5, 1.0, 2.0]
    for i, delay in enumerate([0.0] + backoffs):
        if delay:
            time.sleep(delay)
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
            if resp.status_code in (429, 500, 502, 503, 504):
                # transient; let the loop retry
                last = resp
                continue
            return resp
        except requests.RequestException as e:
            last = e  # type: ignore[assignment]
    # On failure after retries, raise or return last response if available
    if isinstance(last, requests.Response):
        return last
    raise RuntimeError(f"HTTP error after retries: {last}")

def call_once(endpoint: str, api_key: str, model: str, user_text: str,
              effort: Optional[str], temperature: float, max_tokens: int,
              seed: Optional[int], timeout: int) -> Dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_text},
    ]
    body: Dict[str, Any] = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": messages,
    }
    if seed is not None:
        body["seed"] = seed
    if effort is not None:
        body["reasoning_effort"] = effort

    t0 = time.time()
    resp = post_with_retries(endpoint, headers, body, timeout=timeout)
    elapsed_ms = int(round((time.time() - t0) * 1000))

    result: Dict[str, Any] = {
        "status": resp.status_code,
        "latency_ms": elapsed_ms,
        "response_text": None,
        "usage": None,
        "raw": None,
        "error": None,
    }

    try:
        data = resp.json()
    except Exception as e:
        result["error"] = f"Non-JSON response: {resp.text[:200]} ({e})"
        return result

    result["raw"] = data
    if resp.status_code != 200:
        result["error"] = data
        return result

    try:
        text = data["choices"][0]["message"]["content"]
    except Exception:
        text = None
    result["response_text"] = text
    result["usage"] = parse_usage(data)
    return result

def mean(xs):
    vals = [x for x in xs if isinstance(x, (int, float))]
    return sum(vals)/len(vals) if vals else None

def safe_int(x):
    return int(x) if isinstance(x, (int, float)) else None

# ---------- Main ----------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--repeats", type=int, default=DEFAULT_REPEATS,
                        help="Number of repeats per (prompt, effort) pair")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
    parser.add_argument("--max_tokens", type=int, default=DEFAULT_MAX_TOKENS)
    parser.add_argument("--no_seed", action="store_true", help="Do not send seed")
    args = parser.parse_args()

    endpoint = env("ENDPOINT_URL")
    api_key = env("API_KEY")
    model = args.model
    seed = None if args.no_seed else DEFAULT_SEED

    random.seed(2025)
    pairs = []
    for p in PROMPTS:
        for eff in EFFORT_LEVELS:
            for trial in range(args.repeats):
                pairs.append((p, eff, trial))
    random.shuffle(pairs)

    runs_path = "runs.jsonl"
    summary_rows = []
    n_ok = 0
    n_err = 0

    with open(runs_path, "w", encoding="utf-8") as f:
        for p, eff, trial in pairs:
            res = call_once(
                endpoint=endpoint, api_key=api_key, model=model,
                user_text=p["text"], effort=eff, temperature=args.temperature,
                max_tokens=args.max_tokens, seed=seed, timeout=args.timeout
            )
            row = {
                "ts": datetime.utcnow().isoformat(),
                "prompt_id": p["id"],
                "effort": eff if eff is not None else "<unspecified>",
                "trial": trial,
                "status": res["status"],
                "latency_ms": res["latency_ms"],
                "prompt_tokens": (res["usage"] or {}).get("prompt_tokens") if res["usage"] else None,
                "completion_tokens": (res["usage"] or {}).get("completion_tokens") if res["usage"] else None,
                "reasoning_tokens": (res["usage"] or {}).get("reasoning_tokens") if res["usage"] else None,
                "total_tokens": (res["usage"] or {}).get("total_tokens") if res["usage"] else None,
                "text_preview": short(res["response_text"], 120),
                "error": res["error"],
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            if res["error"]:
                n_err += 1
            else:
                n_ok += 1
            summary_rows.append(row)

    # Aggregate means by effort
    by_effort = {}
    for r in summary_rows:
        e = r["effort"]
        by_effort.setdefault(e, {"latency": [], "comp": [], "reason": [], "total": []})
        if r["latency_ms"] is not None:
            by_effort[e]["latency"].append(r["latency_ms"])
        if r["completion_tokens"] is not None:
            by_effort[e]["comp"].append(r["completion_tokens"])
        if r["reasoning_tokens"] is not None:
            by_effort[e]["reason"].append(r["reasoning_tokens"])
        if r["total_tokens"] is not None:
            by_effort[e]["total"].append(r["total_tokens"])

    # Print quick table
    print("\n=== Quick Means by Effort ===")
    print("Effort           | Latency(ms) | OutTokens | ReasoningTokens | TotalTokens")
    print("-----------------+-------------+-----------+------------------+------------")
    def fmt(x):
        return f"{x:.1f}" if isinstance(x, (int, float)) else "-"
    for e in ["<unspecified>", "low", "medium", "high"]:
        mlat = mean(by_effort.get(e, {}).get("latency", []))
        mout = mean(by_effort.get(e, {}).get("comp", []))
        mrea = mean(by_effort.get(e, {}).get("reason", []))
        mtot = mean(by_effort.get(e, {}).get("total", []))
        print(f"{e:16} | {fmt(mlat):>11} | {fmt(mout):>9} | {fmt(mrea):>16} | {fmt(mtot):>10}")

    # Save a compact CSV summary
    csv_path = "summary.csv"
    try:
        import csv
        with open(csv_path, "w", newline="", encoding="utf-8") as cf:
            writer = csv.writer(cf)
            writer.writerow(["effort","mean_latency_ms","mean_completion_tokens","mean_reasoning_tokens","mean_total_tokens"])
            for e in ["<unspecified>", "low", "medium", "high"]:
                mlat = mean(by_effort.get(e, {}).get("latency", []))
                mout = mean(by_effort.get(e, {}).get("comp", []))
                mrea = mean(by_effort.get(e, {}).get("reason", []))
                mtot = mean(by_effort.get(e, {}).get("total", []))
                writer.writerow([e, f"{mlat:.1f}" if mlat else "", f"{mout:.1f}" if mout else "", f"{mrea:.1f}" if mrea else "", f"{mtot:.1f}" if mtot else ""])
        print(f"\nSaved: {csv_path}")
    except Exception as e:
        print(f"[WARN] CSV write failed: {e}")

    print(f"\nSaved raw runs to: {runs_path}")
    print(f"OK: {n_ok}, ERR: {n_err}")
    print("\nInterpretation tip:")
    print("- If '<unspecified>' and 'medium' are nearly identical across latency/tokens, your gateway default is likely 'medium'.")
    print("- Expect tokens/latency trend: low < medium < high (if reasoning tokens are exposed, same order).")

if __name__ == "__main__":
    main()

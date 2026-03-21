import os
from openai import OpenAI
from verdict.core import Experiment
from verdict.judge import LLMJudge
from typing import Any, Callable, Optional, Dict
from dotenv import load_dotenv

# Load environment variables from .env in the workspace (if present)
load_dotenv()

raw_key = os.getenv("OPENAI_API_KEY")
if raw_key:
    raw_key = raw_key.strip().strip('"').strip("'")
client = OpenAI(api_key=raw_key)

MODELS = {
    "gpt-3.5-turbo": "gpt-3.5-turbo",
    "gpt-4o-mini": "gpt-4o-mini",
    "gpt-4.1-mini": "gpt-4.1-mini",
    "gpt-4.1-nano": "gpt-4.1-nano",
    "gpt-5-mini": "gpt-5-mini",
    "gpt-5-nano": "gpt-5-nano"
}
COST_PER_CALL = {
    "gpt-3.5-turbo": 0.003,      # ~$0.003 per call (typical small chat)
    "gpt-4o": 0.005,             # ~$0.005 per call (mid‑range usage)
    "gpt-4o-mini": 0.001,        # ~$0.001 per call (cheapest gpt‑4o variant)
    "gpt-4.1": 0.01,             # ~$0.01 per call (higher‑end gpt‑4.1)
    "gpt-4.1-mini": 0.002,       # ~$0.002 per call
    "gpt-4.1-nano": 0.001,       # ~$0.001 per call (nano tier)
    "o4-mini": 0.001,            # ~$0.001 per call (mini reasoning‑like)
    "gpt-5-mini": 0.002,          # ~$0.002 per call (mini gpt‑5 tier)
    "gpt-5": 0.01,                # ~$0.01 per call (full gpt‑5 reasoning)
    "gpt-5-nano": 0.001,          # ~$0.001 per call (nano reasoning)
}

def judge_llm_call(model_id:str) -> Callable[[str],str]:
    def call(prompt:str) -> str:
        response = client.chat.completions.create(
            model=model_id,
            messages=[{"role":"user","content":prompt}]
        )
        return response.choices[0].message.content
    return call

model_callables= {name: judge_llm_call(mid) for name, mid in MODELS.items()}

judge = LLMJudge(
    llm_call=judge_llm_call,
    cost_per_call=0.003  # Assuming judge calls are cheaper than model calls
)

QUERIES = [
    "Explain the concept of recursion in programming.",
    # "Describe the process of photosynthesis in plants.",
]

if __name__ == "__main__":
    experiment = Experiment(models=model_callables, judge=judge, cost_per_call=COST_PER_CALL)
    results = experiment.run(queries=QUERIES, runs=3, verbose=True)
    results.report()

    print(f"\n Overall winner: {results.winner}")
    print(f"\nPer-model breakdown:")
    for model, stats in results.stats.items():
        print(f" {model}: Quality={stats.quality_mean:.2f}±{stats.quality_std:.2f}, "
              f"Latency={stats.latency_mean:.0f}ms±{stats.latency_std:.0f}ms, "
              f"Cost=${stats.cost_total:.4f}")
    import json
    print("\nFull results as JSON:")
    with open("verdict_results.json", "w") as f:
        json.dump(results.to_dict(), f, indent=2)
    print("Results saved to results.json")
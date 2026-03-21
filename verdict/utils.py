import time
from dataclasses import dataclass , field
from typing import Any, Callable, Optional, Dict

@dataclass
class RunRecord:
    model: str
    query: str
    # run_index: str
    response: str
    quality: float
    latency_ms: float
    cost: float

@dataclass
class ModelStats:
    model: str
    quality_mean: float
    quality_std: float
    latency_mean: float
    latency_std: float
    cost_total: float
    cost_mean: float
    n_runs: int

@dataclass
class Comparison:
    model_a: str
    model_b: str
    metric: str
    
    mean_a: float
    mean_b: float

    t_stat: float
    p_value: float
    cohen_d: float

    ci_low: float
    ci_high: float
    
    winner: Optional[str]

@dataclass
class QueryMin:
    query: str
    winners: Dict[str,int]

def timed_call(fn: Callable, prompt: str) -> tuple[str,float]:
    start = time.perf_counter()
    result = fn(prompt)
    elapsed_ms = (time.perf_counter() -start)*1000

    if isinstance(result, str):
        text= result
    elif isinstance(result,dict):
        text =result.get("text") or result.get("content") or str(result)
    else:
        text = str(result)

    return text, elapsed_ms

def safe_float(value:Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

    






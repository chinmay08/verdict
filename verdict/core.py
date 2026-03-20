from __future__ import annotations
import math
import statistics

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from utils import timed_call, safe_float, QueryMin, Comparison, ModelStats, RunRecord

def _welch_t_test(vals_a: List[float], vals_b: List[float]) -> Tuple[float, float, float, float, float]:

    n_a, n_b = len(vals_a), len(vals_b)
    if n_a < 2 or n_b < 2:
        return 0 , 1, 0, 0, 0
    
    mean_a = statistics.mean(vals_a)
    mean_b = statistics.mean(vals_b)
    var_a = statistics.variance(vals_a)
    var_b = statistics.variance(vals_b)

    se = math.sqrt(var_a/n_a + var_b/n_b)

    if se ==0:
        return 0 , 1, 0, 0, 0
    
    t_stat =(mean_a -mean_b)/se
    
    num = (var_a/n_a + var_b/ n_b)**2
    denom = (var_a/ n_a)**2/(n_a -1) + (var_b/ n_b)**2/(n_b -1)
    df = num / denom if denom > 0 else 1

    p_value = _t_to_p(abs(t_stat),df)

    pooled_std = math.sqrt(
        ((n_a-1)*var_a+(n_b-1)*var_b) / (n_a+n_b-2)
    )


from __future__ import annotations
import math
import statistics

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from .utils import timed_call, safe_float, QueryMin, Comparison, ModelStats, RunRecord

def _welch(vals_a: List[float], vals_b: List[float]) -> Tuple[float, float, float, float, float]:

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


    z = abs(t_stat)
    p = math.erfc(z / math.sqrt(2))
    pooled = math.sqrt(
        ((n_a-1)*var_a+(n_b-1)*var_b) / (n_a+n_b-2)
    )
    cohens_d = (mean_a-mean_b)/ pooled if pooled > 0 else 0

    t_crit = 1.96 if df > 30 else 2+3/df
    diff = mean_a - mean_b
    ci_low = diff - t_crit*se
    ci_high = diff + t_crit*se

    return t_stat, p, cohens_d, ci_low, ci_high

class Results:
    def __init__(self, records: List[RunRecord], model_names: List[str]):
        self.records = records
        self.model_names = model_names
        self.stats : dict[str, ModelStats] = {}
        self.comparisons: List[Comparison] = []
        self.query_wins: List[QueryMin] ={}
        self._analyze()

    def _by_model(self, m): return [r for r in self.records if r.model ==m]

    def _analyze(self):
        for m in self.model_names:
            print(f"Analyzing model {m}...")
            recs = self._by_model(m)
            q = [r.quality for r in recs]
            l = [r.latency_ms for r in recs]
            self.stats[m] = ModelStats(
                model=m,
                quality_mean=statistics.mean(q),
                quality_std=statistics.stdev(q) if len(q) >= 2 else 0,
                latency_mean=statistics.mean(l),
                latency_std=statistics.stdev(l) if len(l) >= 2 else 0,
                cost_total=sum( r.cost for r in recs),
                cost_mean=statistics.mean( r.cost for r in recs),
                n_runs = len(recs),
            )
            print(f" Model {m}: quality={self.stats[m].quality_mean:.2f}±{self.stats[m].quality_std:.2f}")
        for i, a in enumerate(self.model_names):
            print("MODELS",self.model_names)
            for b in self.model_names[i+1:]:
                for metric in ("quality", "latency_ms"):
                    va = [getattr(r,metric) for r in self._by_model(a)]
                    vb = [getattr(r,metric) for r in self._by_model(b)]
                    # print(f" Comparing {a} vs {b} on {metric}...{va} vs {vb}")
                    t, p, d, ci_lo, ci_hi = _welch(va, vb)
                    # print(f"  t={t:.2f} p={p:.4f} d={d:.2f} CI[{ci_lo:.2f}, {ci_hi:.2f}]")
                    winner = None
                    if p < 0.05:
                        if metric == "quality":
                            winner = a if statistics.mean(va) > statistics.mean(vb) else b
                        else:
                            winner = a if statistics.mean(va) < statistics.mean(vb) else b
                    label = "quality" if metric == "quality" else "latency"
                    self.comparisons.append(Comparison(
                        a, b , label, statistics.mean(va), statistics.mean(vb),
                        t,p,d,ci_lo, ci_hi, winner,
                    ))
        queries = sorted(set(r.query for r in self.records))
        for q in queries:
            wins = {m:0 for m in self.model_names}
            q_recs = [r for r in self.records if r.query == q]

            by_round: Dict[int,list] = {}
            for idx, r in enumerate(q_recs):
                rd = idx // len(self.model_names)
                by_round.setdefault(rd,[]).append(r)

                for rd_recs in by_round.values():
                    best = max(rd_recs, key = lambda r:r.quality)
                    wins[best.model]+=1
                self.query_wins[q] = wins
    @property
    def winner(self) -> str: 
        print(self.stats)
        return max(self.stats, key=lambda m: self.stats[m].quality_mean)
    
    def report(self, verbose:bool = True):
        from .display import display_report
        return display_report(self, verbose)
    
    def to_dict(self):
        return {
            "winner":self.winner,
            "stats":{m:vars(s) for m, s in self.stats.items()},
            "comparisons":[vars(c) for c in self.comparisons],
            "query_wins": self.query_wins
        }
class Experiment:
    def __init__(self,models: Dict[str, Callable], judge: Callable, cost_per_call: Optional[dict[str,float]] = None):
        self.models = models
        self.judge = judge
        self.costs = cost_per_call or {}
    def run(self, queries: List[str], runs: int=1, verbose: bool = True):
        names = list(self.models.keys())
        records = []
        total = len(names)*len(queries)*runs

        if verbose:
            print(f"\n VERDICT - {len(names)} models x {len(queries)} queries x {runs} runs = {total}")
        
        done = 0
        for _ in range(runs):
            for q in queries:
                for name, fn in self.models.items():
                    resp, lat = timed_call(fn, q)
                    score = max(1, min(10, safe_float(self.judge(q, resp),5)))

                    records.append(RunRecord(
                        model = name, query = q, response = resp,
                        quality = score, latency_ms = lat,
                        cost = self.costs.get(name,0)
                    ))
                    done+=1
                    if verbose:
                        print(f" [{done}/{total}] {name:<15} score={score:.1f} {lat:.0f}ms")

        if verbose:
            print(f"\n Done. \n")

        return Results(records, names)

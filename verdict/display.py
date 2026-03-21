from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core import Results


def _sig(p):
    if p < 0.001: return "***"
    if p < 0.01: return "***"
    if p < 0.05: return "*"
    return " ns "

def _eff(d):
    d = abs(d)
    if d < 0.2: return "negligible"
    if d < 0.5: return "small"
    if d < 0.8: return "medium"
    return "large"

def display_report(results: "Results", verbose = True):
    out = []
    W = 64

    out.append("="*W)
    out.append(" VERDICT - Benchmark Report".center(W))
    out.append("="*W)

    out.append("")
    out.append(f" {'Model':<15} {'Quality':>8} {'+/- Std': > 7} {'Latency':>9} {'Cost':>8}")
    out.append(" "+"-"*(W-4))

    ranked = sorted(results.stats.values(), key=lambda s: s.quality_mean, reverse = True)
    medals = ["1st", "2nd", "3rd"]+[" "]*20

    for i, s in enumerate(ranked):
        out.append(
            f" {medals[i]} {s.model:<12} "
            f" {s.quality_mean:>7.2f} {s.quality_std:>6.2f} "
            f" {s.latency_mean:>7}ms "
            f"${s.cost_total:>.4f}"
        )
    if results.comparisons:
        out.append("")
        out.append(" STATISTICAL COMPARISONS")
        out.append(" "+"-"*(W-4))
        for c in results.comparisons:
            tag = f"-> {c.winner}" if c.winner else "-> no sig diff"
            out.append(
                f" {c.model_a} vs {c.model_b} [{c.metric}] "
                f"t={c.t_stat:+.2f} p={c.p_value:.4f} {_sig(c.p_value)} "
                f"d={c.cohen_d:+.2f} ({_eff(c.cohen_d)})"
                f"CI[{c.ci_low:+.2f}, {c.ci_high:+.2f}] {tag}"
            )
    if verbose and results.query_wins:
        out.append(" ")
        out.append("WIN RATE PER QUERY")
        out.append(" "+"-"*(W-4))

        models = results.model_names
        hdr = " "+f"{'Query':<30}" + "".join(f"{m:>12}" for m in models)

        out.append(hdr)
        for q, wins in results.query_wins.items():
            total = sum(wins.values())
            cols = "".join(
                f"{wins.get(m,0)}/{total:>2} ({wins.get(m,0)/total*100:.0f}%)".rjust(12)
            )
        label = q if len(q) <= 28 else q[:27]+",,,"
        out.append(f" {label:<30}{cols}")

        out.append("")
        out.append("="*W)
        w = results.winner
        s = results.stats[w]
        out.append(f" WINNER: {w} (quality={s.quality_mean:.2f} latency={s.latency_mean:.0f}ms)")
        out.append("="*W)

        text = "\n".join(out)
        print(text)

        return text
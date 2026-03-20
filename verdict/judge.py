from __future__ import annotations

import re
from typing import Callable, Optional

DEFAULT_JUDGE_PROMPT = """You are an impartial evaluator. Score the following response to the given query on a scale 1 to 10.

CRITERIA:
- Accuracy: Is the information correct ?
- Completeness: Does it fully address the query ?
- Clarity: Is it well written and easy to understand ?
- Relevance: Does it stay on topic?

QUERY:
{query}

RESPONSE:
{response}

Reply with ONLY a JSON object: {{"score": <number>, "reason": "<one sentence>"}}

"""

def _extract_score(text:str) -> float:
    m = re.search(r'"score"\s*:\s*([0-9]+(?:\.[0-9]+)?)\b',text)
    if m:
        return float(m.group(1))
    
    numbers = re.findall(r'\b(\d+(?:\.\d+)?)\b',text)
    for n in numbers:
        val = float(n)
        if 1.0 <= val <= 10.0:
            return val
        
    return 5.0

class LLMJudge:
    def __init__(self,llm_call: Callable[[str],str],prompt_template: Optional[str]=None,cost_per_call: float = 0.0):
        self.llm_call = llm_call
        self.template = prompt_template or DEFAULT_JUDGE_PROMPT
        self.cost_per_call = cost_per_call
        self._total_calls = 0

    def __call__(self, query:str, response: str) -> float:
        prompt = self.template.format(quer=query, response=response)
        raw = self.llm_call(prompt)
        self._total_calls +=1
        return _extract_score(raw if isinstance(raw, str) else str(raw))
    
    @property
    def total_judge_cost(self) -> float:
        return self._total_calls * self.cost_per_call
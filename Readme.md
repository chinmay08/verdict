# Verdict

Verdict is a comprehensive benchmarking tool designed to evaluate and compare the performance of Large Language Models (LLMs) across multiple dimensions including quality, latency, and cost. It provides statistical analysis, pairwise comparisons, and detailed reports to help developers and researchers make informed decisions when selecting AI models for their applications.

## Features

- **Multi-Model Benchmarking**: Compare multiple LLM models simultaneously on the same set of queries.
- **Comprehensive Metrics**: Evaluate models based on quality scores, response latency, and operational costs.
- **Statistical Analysis**: Perform t-tests and effect size calculations for rigorous model comparisons.
- **Automated Judging**: Uses an LLM-based judge to score responses objectively on accuracy, completeness, clarity, and relevance.
- **Detailed Reporting**: Generate human-readable reports with rankings, win rates, and statistical significance.
- **JSON Export**: Save results in JSON format for further analysis or integration.
- **Configurable Costs**: Customize cost calculations per model for accurate budget planning.

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (for model access and judging)

### Dependencies

The following Python packages are required and can be installed via pip:

- `openai` - For interacting with OpenAI's API
- `python-dotenv` - For loading environment variables from .env files

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd dataguardian
   ```

2. Install dependencies:
   ```bash
   pip install openai python-dotenv
   ```

3. Set up your environment:
   - Copy `.env.example` to `.env` (if available) or create a new `.env` file
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     ```

## Usage

### Basic Benchmarking

Run a simple benchmark with the provided test script:

```bash
python test_run.py
```

This will:
- Test 6 different GPT models on 1 query with 3 runs each (18 total evaluations)
- Use an LLM judge to score responses
- Generate a comprehensive report with statistics and comparisons
- Save results to `verdict_results.json`

### Custom Benchmarking

Modify `test_run.py` to customize your benchmarking:

```python
from verdict.core import Experiment
from verdict.judge import LLMJudge

# Define your models and queries
models = {...}  # Your model callables
queries = ["Your query here"]
judge = LLMJudge(llm_call=your_judge_function)

# Run experiment
experiment = Experiment(models=models, judge=judge, cost_per_call=cost_dict)
results = experiment.run(queries=queries, runs=3, verbose=True)
results.report()
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)

### Cost Configuration

Update the `COST_PER_CALL` dictionary in your script to reflect current pricing for each model.

### Judge Configuration

Customize the judging criteria by modifying the `DEFAULT_JUDGE_PROMPT` in `verdict/judge.py` or pass a custom prompt template to `LLMJudge`.

## Output Example

```
VERDICT - 6 models x 1 queries x 3 runs = 18
[1/18] gpt-3.5-turbo   score=5.0  2757ms
[2/18] gpt-4o-mini     score=5.0  8089ms
...
================================================================
                   VERDICT - Benchmark Report
================================================================

Model            Quality +/- Std   Latency     Cost
------------------------------------------------------------
1st gpt-3.5-turbo     5.00   0.00  2382.53ms $0.0090
2nd gpt-4o-mini      5.00   0.00  8550.42ms $0.0030
...

WINNER: gpt-3.5-turbo (quality=5.00 latency=2383ms)
```

## Project Structure

```
dataguardian/
├── verdict/
│   ├── core.py      # Main experiment logic and statistical analysis
│   ├── judge.py     # LLM-based judging system
│   ├── display.py   # Report generation and formatting
│   └── utils.py     # Utility functions and data structures
├── test_run.py      # Example benchmarking script
├── verdict_results.json  # Output results file
├── .env             # Environment variables (not committed)
└── Readme.md        # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

- **Python-dotenv parsing error**: Ensure your `.env` file is properly formatted. The API key should be on a single line without extra quotes.
- **OpenAI API errors**: Verify your API key is valid and has sufficient credits.
- **Model not found**: Check that the model names in your configuration match available OpenAI models.

## Future Enhancements

- Support for additional LLM providers (Anthropic, Google, etc.)
- Web-based dashboard for result visualization
- Custom scoring rubrics
- Integration with CI/CD pipelines for automated benchmarking
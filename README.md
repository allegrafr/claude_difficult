# Claude Difficult MMLU-Pro Subset

This repository contains a prepared subset of difficult MMLU-Pro questions for evaluation with Claude.

The subset contains questions that were previously answered incorrectly by both Qwen and Llama. Each row in `claude_ready_prompts.csv` already includes a fully formatted prompt, so the runner only needs to read the `prompt` column, call Claude, and save the response.

## Files

| File | Purpose |
|---|---|
| `claude_ready_prompts.csv` | Prepared 5,789-question subset with one Claude-ready prompt per row |
| `run_claude_prompts.py` | Python script that calls Claude and saves results |
| `claude_results.csv` | Output file created after running the script |
| `claude_wrong_only.csv` | Output file created after running the script, containing only incorrect Claude answers |

## Default settings

The runner uses these defaults:

```text
MODEL_NAME = claude-sonnet-4-6
TEMPERATURE = 0
MAX_TOKENS = 600
SAVE_EVERY = 50
SLEEP_SECONDS = 0.5
```

These can be changed with environment variables.

## Setup

Install the required packages:

```bash
pip install pandas anthropic
```

Set the Anthropic API key.

Unix-style shell:

```bash
export ANTHROPIC_API_KEY="your_key_here"
```

Windows PowerShell:

```powershell
$env:ANTHROPIC_API_KEY="your_key_here"
```

## Recommended test run

Run a small 50-question test first:

Unix-style shell:

```bash
python run_claude_prompts.py claude_ready_prompts.csv --rows 50
```

Windows PowerShell:

```powershell
python run_claude_prompts.py claude_ready_prompts.csv --rows 50
```

This creates:

```text
claude_results.csv
claude_wrong_only.csv
```

Please check that Claude is returning valid JSON with this format:

```json
{
  "predicted_answer": "A",
  "reasoning": "brief explanation"
}
```

If the test output looks correct, delete the two test output files before running the full subset:

```text
claude_results.csv
claude_wrong_only.csv
```

## Full run

Run the full prepared subset:

```bash
python run_claude_prompts.py claude_ready_prompts.csv
```

The script saves progress every 50 newly processed questions and once at the end.

If the run stops midway, run the same command again. The script will skip question IDs already present in `claude_results.csv`.

## Output files

### `claude_results.csv`

Full Claude results with these columns:

```text
question_id
correct_answer
predicted_answer
reasoning
question
options
category
source
raw_response
error
```

### `claude_wrong_only.csv`

Only the questions Claude answered incorrectly, with these columns:

```text
question_id
question
options
correct_answer
predicted_answer
category
source
```

## Changing the model or settings

Use a different Claude model:

Unix-style shell:

```bash
MODEL_NAME="claude-opus-4-8" python run_claude_prompts.py claude_ready_prompts.csv --rows 50
```

Windows PowerShell:

```powershell
$env:MODEL_NAME="claude-opus-4-8"; python run_claude_prompts.py claude_ready_prompts.csv --rows 50
```

Change max output tokens:

Unix-style shell:

```bash
MAX_TOKENS=1000 python run_claude_prompts.py claude_ready_prompts.csv --rows 50
```

Windows PowerShell:

```powershell
$env:MAX_TOKENS="1000"; python run_claude_prompts.py claude_ready_prompts.csv --rows 50
```

Change save interval:

Unix-style shell:

```bash
SAVE_EVERY=25 python run_claude_prompts.py claude_ready_prompts.csv
```

Windows PowerShell:

```powershell
$env:SAVE_EVERY="25"; python run_claude_prompts.py claude_ready_prompts.csv
```

## Notes for runner

This script uses the official Anthropic Python SDK by default. If Claude is accessed through another backend, such as AWS Bedrock, Vertex AI, OpenRouter, or an internal lab endpoint, only the `call_claude()` function should need to be adapted. The CSV itself is already prepared and should not require preprocessing.

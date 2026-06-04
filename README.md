# Claude Difficult MMLU-Pro Subset

This repository contains a prepared subset of difficult MMLU-Pro questions for Claude evaluation.

The subset contains **5,789 questions** that were answered incorrectly by both Qwen and Llama. Each row in `claude_ready_prompts.csv` already includes a fully formatted prompt in the `prompt` column, so no MMLU-Pro download, filtering, or prompt construction is needed before calling Claude.

## Files

| File | Purpose |
|---|---|
| `claude_ready_prompts.csv` | Prepared input file. The `prompt` column is the exact text to send to Claude. |
| `run_claude_prompts.py` | Python script that reads the CSV, calls Claude, and saves the results. |
| `requirements.txt` | Python dependencies. |

## Default settings

```text
MODEL_NAME = claude-sonnet-4-6
temperature = 0
max_tokens = 600
save every 50 newly processed questions
```

The script saves progress every 50 newly processed questions and once more at the end. If restarted, it skips question IDs already present in `claude_results.csv`.

## Setup and run

Clone the repository and install the dependencies:

```bash
git clone https://github.com/allegrafr/claude_difficult.git
cd claude_difficult
pip install -r requirements.txt
```

Set `ANTHROPIC_API_KEY` in the environment using your preferred shell, credential manager, or lab setup.

Example for Unix-style shells:

```bash
export ANTHROPIC_API_KEY="your_key_here"
```

Example for Windows PowerShell:

```powershell
$env:ANTHROPIC_API_KEY="your_key_here"
```

Start with a 50-question test run:

```bash
python run_claude_prompts.py claude_ready_prompts.csv --rows 50
```

If the test output looks correct, delete `claude_results.csv` and `claude_wrong_only.csv`, then run the full subset:

```bash
python run_claude_prompts.py claude_ready_prompts.csv
```

## Output files

The script creates two output files:

| File | Contents |
|---|---|
| `claude_results.csv` | Full results with `question_id`, `correct_answer`, `predicted_answer`, `reasoning`, `question`, `options`, `category`, `source`, `raw_response`, and `error`. |
| `claude_wrong_only.csv` | Only the questions Claude answered incorrectly, with `question_id`, `question`, `options`, `correct_answer`, `predicted_answer`, `category`, and `source`. |

After the run finishes, please send back both output files.

## Optional overrides

The defaults can be changed with environment variables if needed:

```bash
MODEL_NAME="claude-sonnet-4-6" MAX_TOKENS=1000 SAVE_EVERY=50 python run_claude_prompts.py claude_ready_prompts.csv --rows 50
```

Available overrides:

```text
MODEL_NAME
MAX_TOKENS
SAVE_EVERY
SLEEP_SECONDS
```

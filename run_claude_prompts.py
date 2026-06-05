import argparse
import json
import os
import time

import pandas as pd
from anthropic import Anthropic


RESULTS_FILE = "claude_results.csv"
WRONG_ONLY_FILE = "claude_wrong_only.csv"

MODEL_NAME = os.environ.get("MODEL_NAME", "claude-sonnet-4-6")
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "600"))
SLEEP_SECONDS = float(os.environ.get("SLEEP_SECONDS", "0.5"))
SAVE_EVERY = int(os.environ.get("SAVE_EVERY", "50"))


def normalize_answer(value):
    if pd.isna(value):
        return ""

    value = str(value).strip().upper()
    return value[0] if value else ""


def extract_json(text):
    text = str(text).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass

    return {
        "predicted_answer": "",
        "reasoning": text,
    }


def call_claude(client, prompt):
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=MAX_TOKENS,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response.content[0].text


def save_outputs(results):
    results_df = pd.DataFrame(results)
    results_df.to_csv(RESULTS_FILE, index=False)

    wrong_df = results_df[
        results_df["predicted_answer"] != results_df["correct_answer"]
    ].copy()

    wrong_columns = [
        "question_id",
        "question",
        "options",
        "correct_answer",
        "predicted_answer",
        "category",
        "source",
    ]

    wrong_df[wrong_columns].to_csv(WRONG_ONLY_FILE, index=False)


def load_existing_results():
    if not os.path.exists(RESULTS_FILE):
        return [], set()

    existing = pd.read_csv(RESULTS_FILE)

    if "question_id" not in existing.columns:
        return [], set()

    done_ids = set(existing["question_id"].astype(str))
    return existing.to_dict("records"), done_ids


def validate_input(df):
    required_columns = [
        "question_id",
        "correct_answer",
        "question",
        "options",
        "category",
        "source",
        "prompt",
    ]

    missing = [column for column in required_columns if column not in df.columns]

    if missing:
        raise ValueError(f"Input CSV is missing required columns: {missing}")


def main():
    parser = argparse.ArgumentParser(
        description="Run Claude on a prepared CSV of prompts."
    )
    parser.add_argument(
        "input_file",
        help="Path to the prepared input CSV file, such as claude_ready_prompts.csv",
    )
    parser.add_argument(
        "--rows",
        type=int,
        default=None,
        metavar="N",
        help="Maximum number of rows to process for a test run. Default: all rows.",
    )

    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set.")

    client = Anthropic(api_key=api_key)

    df = pd.read_csv(args.input_file)
    validate_input(df)

    if args.rows is not None:
        df = df.head(args.rows)

    results, done_ids = load_existing_results()
    processed_since_save = 0

    for _, row in df.iterrows():
        question_id = str(row["question_id"])

        if question_id in done_ids:
            print(f"Skipping already completed question_id={question_id}")
            continue

        print(f"Running {len(results) + 1}/{len(df)} | question_id={question_id}")

        raw_response = ""
        predicted_answer = ""
        reasoning = ""
        error = ""

        try:
            raw_response = call_claude(client, row["prompt"])
            parsed = extract_json(raw_response)
            predicted_answer = normalize_answer(parsed.get("predicted_answer", ""))
            reasoning = str(parsed.get("reasoning", ""))
        except Exception as e:
            error = str(e)
            reasoning = f"ERROR: {error}"

        results.append(
            {
                "question_id": row["question_id"],
                "correct_answer": normalize_answer(row["correct_answer"]),
                "predicted_answer": predicted_answer,
                "reasoning": reasoning,
                "question": row["question"],
                "options": row["options"],
                "category": row["category"],
                "source": row["source"],
                "raw_response": raw_response,
                "error": error,
            }
        )

        done_ids.add(question_id)
        processed_since_save += 1

        if processed_since_save >= SAVE_EVERY:
            save_outputs(results)
            print(f"Progress saved after {processed_since_save} new questions.")
            processed_since_save = 0

        time.sleep(SLEEP_SECONDS)

    save_outputs(results)

    print("Finished.")
    print(f"Saved all results to: {RESULTS_FILE}")
    print(f"Saved wrong-only results to: {WRONG_ONLY_FILE}")


if __name__ == "__main__":
    main()

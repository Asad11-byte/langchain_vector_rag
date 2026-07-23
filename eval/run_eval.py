"""
RAGAS evaluation script.

Runs your golden Q&A dataset through the live RAG pipeline (retrieval +
generation), then scores the results using RAGAS metrics:

  Retrieval quality:
    - context_precision  -> are the retrieved chunks actually relevant?
    - context_recall     -> did retrieval find everything needed to answer?

  Generation quality:
    - faithfulness       -> is the answer grounded in the retrieved context
                             (i.e. not hallucinated)?
    - answer_relevancy   -> does the answer actually address the question?

Usage (from project root):
    python eval/run_eval.py

Or trigger via the API: POST /api/eval/run
"""

import json
import sys
import os
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    from datasets import Dataset  # type: ignore[import]
except ImportError as exc:
    raise ImportError(
        "The `datasets` library is required to run this script. "
        "Install it with `pip install datasets`."
    ) from exc

from ragas import evaluate  # type: ignore[import]
from ragas.metrics import (  # type: ignore[import]
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)

from app.core.chain import answer_question

GOLDEN_DATASET_PATH = os.path.join(os.path.dirname(__file__), "golden_dataset.json")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")


def load_golden_dataset() -> list[dict]:
    with open(GOLDEN_DATASET_PATH, "r") as f:
        return json.load(f)


def build_ragas_dataset(golden_qa: list[dict], use_query_rewrite: bool = False, rerank_method: str = "local") -> Dataset:
    """
    Runs each golden question through the live RAG pipeline and assembles
    the {question, answer, contexts, ground_truth} format RAGAS expects.
    """
    questions, answers, contexts, ground_truths = [], [], [], []

    for item in golden_qa:
        result = answer_question(
            question=item["question"],
            use_query_rewrite=use_query_rewrite,
            rerank_method=rerank_method,
        )

        questions.append(item["question"])
        answers.append(result["answer"])
        contexts.append([s["text"] for s in result["sources"]])
        ground_truths.append(item["ground_truth"])

    return Dataset.from_dict(
        {
            "question": questions,
            "answer": answers,
            "contexts": contexts,
            "ground_truth": ground_truths,
        }
    )


def run_ragas_eval(use_query_rewrite: bool = False, rerank_method: str = "local", save_results: bool = True) -> dict:
    """
    Main entry point. Returns a dict of aggregate metric scores.
    Also saves a timestamped JSON file under eval/results/ for tracking
    experiment history (chunking/reranking/rewriting comparisons).
    """
    golden_qa = load_golden_dataset()

    if not golden_qa or "Replace with" in golden_qa[0]["question"]:
        raise ValueError(
            "golden_dataset.json still contains placeholder data. "
            "Add real questions/answers based on your uploaded documents first."
        )

    dataset = build_ragas_dataset(golden_qa, use_query_rewrite, rerank_method)

    result = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
    )

    scores = result.to_pandas()[
        ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
    ].mean().to_dict()

    if save_results:
        os.makedirs(RESULTS_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_config = {"use_query_rewrite": use_query_rewrite, "rerank_method": rerank_method}

        output = {"timestamp": timestamp, "config": run_config, "metrics": scores}

        out_path = os.path.join(RESULTS_DIR, f"eval_{timestamp}.json")
        with open(out_path, "w") as f:
            json.dump(output, f, indent=2)

        print(f"Results saved to {out_path}")

    return scores


if __name__ == "__main__":
    print("Running RAGAS evaluation...")
    scores = run_ragas_eval()
    print("\n--- Results ---")
    for metric, value in scores.items():
        print(f"{metric}: {value:.3f}")

"""
Eval endpoint: triggers a RAGAS evaluation run against the golden dataset
and returns the metrics. Actual eval logic lives in eval/run_eval.py so it
can also be run standalone from the command line.
"""

from fastapi import APIRouter, HTTPException
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

router = APIRouter()


@router.post("/eval/run")
async def run_evaluation():
    """Runs the RAGAS evaluation suite and returns aggregate metrics."""
    try:
        from eval.run_eval import run_ragas_eval
        results = run_ragas_eval()
        return {"status": "completed", "metrics": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eval failed: {str(e)}")

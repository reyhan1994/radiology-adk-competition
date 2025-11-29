#!/usr/bin/env python3
"""
Robust master script for the Radiology ADK repo.
Usage:
  python src/master_agent.py --input images --output submission.csv
This script:
- ensures src/ is on PYTHONPATH so imports like `from agents...` work
- finds image files in input folder
- runs the master SequentialAgent workflow (works for sync or async `run`)
- writes submission.csv with per-image outputs
"""

import os
import sys
import argparse
import csv
import asyncio
import inspect

# ---------------------------
# Make sure the src/ directory is importable
# ---------------------------
# __file__ is src/master_agent.py -> parent is src/
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# ---------------------------
# Imports from your repo (should now resolve)
# ---------------------------
try:
    from adk.agent import SequentialAgent
    from adk.step import Step
except Exception as e:
    # If package names differ, raise clear error
    raise ImportError(
        "Cannot import adk package. Make sure src/adk exists and contains agent.py and step.py. Original error: "
        + str(e)
    )

# Import agents
from agents.patient_context_agent import PatientContextAgent
from agents.image_analysis_agent import ImageAnalysisAgent
from agents.report_generation_agent import ReportGenerationAgent
from agents.pathology_coding_agent import PathologyCodingAgent
from agents.memory_consolidation_agent import MemoryConsolidationAgent

# ---------------------------
# Helper: unwrap possible StepResult-like objects
# ---------------------------
def _unwrap(v):
    # If returned object carries .output (StepResult), extract it
    try:
        if hasattr(v, "output"):
            return v.output
    except Exception:
        pass
    return v

# ---------------------------
# Create workflow (use your repository's adk.Step and SequentialAgent)
# ---------------------------
steps = [
    Step("get_patient_context", PatientContextAgent, "user_request", "patient_data"),
    Step("run_image_analysis", ImageAnalysisAgent, "user_request", "analysis_findings"),
    Step("generate_final_report", ReportGenerationAgent, ["patient_data", "analysis_findings"], "final_report"),
    Step("run_pathology_coding", PathologyCodingAgent, "final_report", "coding_result"),
    Step("store_long_term_memory", MemoryConsolidationAgent, "final_report", "memory_status"),
]

master_agent = SequentialAgent(steps)

# ---------------------------
# Run the agent for a single image (handles sync/async implementations)
# ---------------------------
def run_for_one(input_value):
    """
    input_value: typically image path or identifier that agents expect (we pass image path)
    returns: dict of artifacts (unwrapped)
    """
    # prepare initial artifacts
    initial = {"user_request": input_value}

    # master_agent.run may be async or sync
    run_fn = getattr(master_agent, "run", None)
    if run_fn is None:
        raise RuntimeError("master_agent has no run() method.")

    if inspect.iscoroutinefunction(run_fn):
        artifacts = asyncio.run(run_fn(initial))
    else:
        maybe = run_fn(initial)
        # if returned coroutine object
        if inspect.isawaitable(maybe):
            artifacts = asyncio.run(maybe)
        else:
            artifacts = maybe

    # unwrap StepResult-like values if present
    artifacts_unwrapped = {}
    if isinstance(artifacts, dict):
        for k, v in artifacts.items():
            artifacts_unwrapped[k] = _unwrap(v)
    else:
        # if some other structure, try best-effort
        artifacts_unwrapped = _unwrap(artifacts)
    return artifacts_unwrapped

# ---------------------------
# Utilities: find images
# ---------------------------
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".dcm"}  # include DICOM ext if used

def list_images(folder):
    files = []
    for fn in sorted(os.listdir(folder)):
        if os.path.splitext(fn.lower())[1] in IMAGE_EXTS:
            files.append(fn)
    return files

# ---------------------------
# Main CLI
# ---------------------------
def main(input_folder, output_csv):
    if not os.path.isdir(input_folder):
        raise FileNotFoundError(f"Input folder not found: {input_folder}")

    images = list_images(input_folder)
    if not images:
        print("No images found in", input_folder)
        # create empty CSV with header
        with open(output_csv, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["image", "analysis_pathology", "analysis_confidence", "final_report", "ICD_10", "CPT", "memory_status"])
        print(f"Empty submission created: {output_csv}")
        return

    rows = []
    for img in images:
        img_path = os.path.join(input_folder, img)
        print("Processing:", img_path)
        artifacts = run_for_one(img_path)

        # safe extraction with defaults
        analysis = artifacts.get("analysis_findings", {}) or {}
        # sometimes analysis_findings may be nested with keys; try unwrap again
        pathology = analysis.get("pathology") if isinstance(analysis, dict) else None
        confidence = analysis.get("confidence") if isinstance(analysis, dict) else None

        final_report = artifacts.get("final_report", "")
        coding = artifacts.get("coding_result", {}) or {}
        icd = coding.get("ICD_10_Code") or coding.get("ICD_10") or ""
        cpt = coding.get("CPT_Code") or coding.get("CPT") or ""
        memory_status = artifacts.get("memory_status", "")

        rows.append({
            "image": img,
            "analysis_pathology": pathology,
            "analysis_confidence": confidence,
            "final_report": final_report,
            "ICD_10": icd,
            "CPT": cpt,
            "memory_status": memory_status
        })

    # Write CSV
    fieldnames = ["image", "analysis_pathology", "analysis_confidence", "final_report", "ICD_10", "CPT", "memory_status"]
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"✅ CSV generated: {output_csv} (rows: {len(rows)})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i", required=True, help="Path to input images folder (local)")
    parser.add_argument("--output", "-o", default="submission.csv", help="Output CSV file path")
    args = parser.parse_args()
    main(args.input, args.output)

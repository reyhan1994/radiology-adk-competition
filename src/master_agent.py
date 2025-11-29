#!/usr/bin/env python3
"""
master_agent.py

Robust runner that:
- makes sure src/ is on PYTHONPATH so local imports work
- constructs a SequentialAgent workflow using your agents (instances)
- iterates over images in the input folder and runs the workflow per image
- writes a submission CSV with key fields

Usage:
    python src/master_agent.py --input images --output submission.csv
"""

import os
import sys
import argparse
import csv
import traceback

# Ensure the current file's directory (src/) is on sys.path so "from agents..." works
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Now import ADK components and your agents
try:
    from adk.agent import SequentialAgent
    from adk.step import Step
except Exception as e:
    raise ImportError(
        "Failed to import adk. Ensure src/adk exists and contains agent.py and step.py. Original error: "
        + str(e)
    )

# Import agent classes (they should be defined as classes with run(self, input_data))
try:
    from agents.patient_context_agent import PatientContextAgent
    from agents.image_analysis_agent import ImageAnalysisAgent
    from agents.report_generation_agent import ReportGenerationAgent
    from agents.pathology_coding_agent import PathologyCodingAgent
    from agents.memory_consolidation_agent import MemoryConsolidationAgent
except Exception as e:
    raise ImportError(
        "Failed to import one of the agent modules from src/agents. "
        "Make sure files exist and define the correct classes. Original error: " + str(e)
    )


IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".dcm"}


def list_images(folder):
    """Return sorted list of image filenames (not full paths) in folder with supported extensions."""
    names = []
    if not os.path.isdir(folder):
        return names
    for fn in sorted(os.listdir(folder)):
        _, ext = os.path.splitext(fn.lower())
        if ext in IMAGE_EXTS:
            names.append(fn)
    return names


def safe_get(d, *keys, default=None):
    """Safely navigate dict-like structures. If intermediate is not dict returns default."""
    cur = d
    for k in keys:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return default
    return cur


def run_workflow_for_image(master_agent, image_path):
    """
    Calls master_agent.run with initial artifacts {'user_request': image_path}
    Expects a dict result (artifacts).
    Returns artifacts dict (never raises unless something catastrophic happens).
    """
    initial = {"user_request": image_path}
    try:
        # master_agent.run may be sync and return a dict
        result = master_agent.run(initial)
        # result should be a dict
        if not isinstance(result, dict):
            # try to convert or wrap
            return {"final_result": result}
        return result
    except Exception:
        # capture a traceback string for logging in CSV if needed
        tb = traceback.format_exc()
        return {"error": tb}


def build_master_agent():
    """
    Construct the list of Step objects using agent instances (not classes).
    Important: Step signature in this repo is Step(name, agent_instance, input_key, output_key)
    """
    # create agent instances
    pat_agent = PatientContextAgent()
    img_agent = ImageAnalysisAgent()
    report_agent = ReportGenerationAgent()
    code_agent = PathologyCodingAgent()
    mem_agent = MemoryConsolidationAgent()

    # build steps (pass instances)
    steps = [
        Step("get_patient_context", pat_agent, "user_request", "patient_data"),
        Step("run_image_analysis", img_agent, "user_request", "analysis_findings"),
        Step("generate_final_report", report_agent, ["patient_data", "analysis_findings"], "final_report"),
        Step("run_pathology_coding", code_agent, "final_report", "coding_result"),
        Step("store_long_term_memory", mem_agent, "final_report", "memory_status"),
    ]

    master = SequentialAgent(steps)
    return master


def extract_row_from_artifacts(image_name, artifacts):
    """
    Normalize artifacts into CSV row columns:
    image, analysis_pathology, analysis_confidence, final_report, ICD_10, CPT, memory_status, error
    """
    # defaults
    pathology = safe_get(artifacts, "analysis_findings", "pathology", default="")
    confidence = safe_get(artifacts, "analysis_findings", "confidence", default="")
    final_report = artifacts.get("final_report", "")
    coding = artifacts.get("coding_result", {}) or {}
    icd = coding.get("ICD_10_Code") or coding.get("ICD_10") or ""
    cpt = coding.get("CPT_Code") or coding.get("CPT") or ""
    memory_status = artifacts.get("memory_status", "")
    error = artifacts.get("error", "")

    return {
        "image": image_name,
        "analysis_pathology": pathology,
        "analysis_confidence": confidence,
        "final_report": final_report,
        "ICD_10": icd,
        "CPT": cpt,
        "memory_status": memory_status,
        "error": error,
    }


def main(input_folder, output_csv):
    if not os.path.isdir(input_folder):
        raise FileNotFoundError(f"Input folder does not exist: {input_folder}")

    images = list_images(input_folder)
    print(f"Found {len(images)} image(s) in '{input_folder}'.")

    # build master agent
    master_agent = build_master_agent()

    rows = []
    for img in images:
        image_path = os.path.join(input_folder, img)
        print(f"Processing: {image_path}")
        artifacts = run_workflow_for_image(master_agent, image_path)
        row = extract_row_from_artifacts(img, artifacts)
        rows.append(row)

    # Define CSV fieldnames
    fieldnames = [
        "image",
        "analysis_pathology",
        "analysis_confidence",
        "final_report",
        "ICD_10",
        "CPT",
        "memory_status",
        "error",
    ]

    # Write CSV
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"✅ CSV written to: {output_csv} (rows: {len(rows)})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Radiology ADK master workflow over images folder.")
    parser.add_argument("--input", "-i", required=True, help="Path to input images folder (relative to repo root).")
    parser.add_argument("--output", "-o", default="submission.csv", help="Output CSV file path.")
    args = parser.parse_args()
    main(args.input, args.output)

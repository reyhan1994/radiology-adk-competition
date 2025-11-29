import os
import csv
from adk.agent import SequentialAgent
from adk.step import Step

from agents.patient_context_agent import PatientContextAgent
from agents.image_analysis_agent import ImageAnalysisAgent
from agents.pathology_coding_agent import PathologyCodingAgent
from agents.report_generation_agent import ReportGenerationAgent

import argparse

def load_images(folder):
    files = []
    for name in os.listdir(folder):
        if name.lower().endswith((".png", ".jpg", ".jpeg")):
            files.append(os.path.join(folder, name))
    return files

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    args = parser.parse_args()

    images = load_images(args.input)

    steps = [
        PatientContextAgent(),
        ImageAnalysisAgent(),
        PathologyCodingAgent(),
        ReportGenerationAgent(),
    ]

    pipeline = SequentialAgent()
    results = pipeline.run(steps, images)

    with open(args.output, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["image", "patient_context", "analysis", "icd10", "report"])
        for img in images:
            r = results
            writer.writerow([
                os.path.basename(img),
                r["patient_context"],
                r["analysis"],
                r["icd10"],
                r["report"]
            ])

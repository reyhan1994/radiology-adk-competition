from adk.agent import SequentialAgent
from adk.step import Step
from agents.patient_context_agent import PatientContextAgent
from agents.image_analysis_agent import ImageAnalysisAgent
from agents.report_generation_agent import ReportGenerationAgent
from agents.pathology_coding_agent import PathologyCodingAgent
from agents.memory_consolidation_agent import MemoryConsolidationAgent

class RadiologyMasterAgent(SequentialAgent):
    def define_workflow(self):
        return [
            Step("get_patient_context", PatientContextAgent(), input_key="user_request", output_key="patient_data"),
            Step("run_image_analysis", ImageAnalysisAgent(), input_key="user_request", output_key="analysis_findings"),
            Step("generate_final_report", ReportGenerationAgent(), input_key=["patient_data","analysis_findings"], output_key="final_report"),
            Step("run_pathology_coding", PathologyCodingAgent(), input_key="final_report", output_key="coding_result"),
            Step("store_long_term_memory", MemoryConsolidationAgent(), input_key="final_report", output_key="memory_status"),
        ]

if __name__ == "__main__":
    import pandas as pd
    import os

    input_folder = "images"
    output_file = "submission.csv"

    master_agent = RadiologyMasterAgent()
    results = []

    for image_file in os.listdir(input_folder):
        image_path = os.path.join(input_folder, image_file)
        output = master_agent.run({"user_request": image_path})
        results.append({
            "image": image_file,
            "diagnosis": output["analysis_findings"]["pathology"],
            "ICD": output["coding_result"]["ICD_10_Code"]
        })

    pd.DataFrame(results).to_csv(output_file, index=False)
    print(f"✅ CSV generated: {output_file}")

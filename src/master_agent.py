from adk.agent import SequentialAgent
from adk.step import Step
from src.agents.patient_context_agent import PatientContextAgent
from src.agents.image_analysis_agent import ImageAnalysisAgent
from src.agents.report_generation_agent import ReportGenerationAgent
from src.agents.pathology_coding_agent import PathologyCodingAgent
from src.agents.memory_consolidation_agent import MemoryConsolidationAgent

# Instantiate agents
patient_context_agent = PatientContextAgent()
image_analysis_agent = ImageAnalysisAgent()
report_generation_agent = ReportGenerationAgent()
pathology_coding_agent = PathologyCodingAgent()
memory_consolidation_agent = MemoryConsolidationAgent()

class RadiologyMasterAgent(SequentialAgent):
    def define_workflow(self) -> list[Step]:
        return [
            Step(
                name="get_patient_context",
                agent=patient_context_agent,
                input_key="user_request",
                output_key="patient_data"
            ),
            Step(
                name="run_image_analysis",
                agent=image_analysis_agent,
                input_key="user_request",
                output_key="analysis_findings"
            ),
            Step(
                name="generate_final_report",
                agent=report_generation_agent,
                input_key=["patient_data", "analysis_findings"],
                output_key="final_report"
            ),
            Step(
                name="run_pathology_coding",
                agent=pathology_coding_agent,
                input_key="final_report",
                output_key="coding_result"
            ),
            Step(
                name="store_long_term_memory",
                agent=memory_consolidation_agent,
                input_key="final_report",
                output_key="memory_status"
            )
        ]

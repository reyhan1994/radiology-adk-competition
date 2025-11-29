# src/agents/report_generation_agent.py
class ReportGenerationAgent:
    def run(self, input_data):
        # input_data is a dict: {"patient_data": {...}, "analysis_findings": {...}} (because Step passed list keys)
        patient = input_data.get("patient_data", {}) if isinstance(input_data, dict) else {}
        analysis = input_data.get("analysis_findings", {}) if isinstance(input_data, dict) else {}
        report = f"Final Report: {analysis.get('pathology', 'No finding')} for patient {patient.get('name', 'N/A')}."
        return report  # will be stored as artifacts['final_report']

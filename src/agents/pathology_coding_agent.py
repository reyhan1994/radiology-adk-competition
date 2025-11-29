# src/agents/pathology_coding_agent.py
class PathologyCodingAgent:
    def run(self, input_data):
        # input_data is final_report string or dict containing final_report
        report = input_data if isinstance(input_data, str) else input_data.get("final_report", "")
        if "Pneumothorax" in report:
            return {"ICD_10_Code": "J93.9", "CPT_Code": "71045"}
        return {}

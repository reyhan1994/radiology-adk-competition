# src/agents/patient_context_agent.py
class PatientContextAgent:
    def run(self, input_data):
        # input_data will be the user_request (e.g., image path or id)
        patient_id = None
        if isinstance(input_data, dict):
            patient_id = input_data.get("user_request") or input_data.get("patient_id")
        else:
            patient_id = input_data

        # return the patient_data dict (assigned to artifacts['patient_data'])
        return {"patient_id": str(patient_id), "name": "Ali Ahmadi", "age": 45}

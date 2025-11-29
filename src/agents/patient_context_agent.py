from adk.agent import BaseAgent


def retrieve_patient_history(patient_id: str):
    # Simulate retrieving patient info from EMR
    return {"patient_id": patient_id, "name": "Ali Ahmadi", "age": 45}

class PatientContextAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="patient_context_agent",
            function=retrieve_patient_history
        )

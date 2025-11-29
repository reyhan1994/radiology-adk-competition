from adk.step import Step

class PatientContextAgent(Step):
    def __init__(self):
        super().__init__("patient_context")

    def run(self, input_data):
        return {"patient_context": "No context available"}

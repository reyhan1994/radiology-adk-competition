from adk.agent import SequentialAgent
from adk.step import Step

class PatientContextAgent(SequentialAgent):
    def __init__(self):
        steps = [
            Step(
                name="extract_patient_context",
                prompt="Extract patient age, sex, and clinical information from the radiology case.",
                model="gpt-4o-mini"
            )
        ]
        super().__init__(steps)

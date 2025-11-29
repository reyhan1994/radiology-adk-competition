from adk.step import Step

class PathologyCodingAgent(Step):
    def __init__(self):
        super().__init__("pathology_coding")

    def run(self, input_data):
        return {"icd10": "R93.8"}


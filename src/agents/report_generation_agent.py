from adk.step import Step

class ReportGenerationAgent(Step):
    def __init__(self):
        super().__init__("report_generation")

    def run(self, input_data):
        return {"report": "No abnormalities detected"}

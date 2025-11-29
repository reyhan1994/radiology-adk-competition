from adk.step import Step

class ImageAnalysisAgent(Step):
    def __init__(self):
        super().__init__("image_analysis")

    def run(self, input_data):
        return {"analysis": f"Processed {len(input_data)} images"}

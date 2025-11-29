import time
from adk.agent import Agent, StepResult

class ImageAnalysisAgent(Agent):
    async def run(self, artifacts) -> StepResult:
        print("⚠️ Starting image analysis... (simulated LRO)")  # LRO simulated
        time.sleep(4)

        findings = {
            "pathology": "Pneumothorax (Left Upper Lobe)",
            "confidence": "95%"
        }
        return StepResult(output={"analysis_findings": findings})

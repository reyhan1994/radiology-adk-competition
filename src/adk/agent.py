# src/adk/agent.py
import asyncio
from typing import Any, Dict

class StepResult:
   
    def __init__(self, output: Any):
        self.output = output

class SequentialAgent:
    def __init__(self, steps=None):
        # steps: list of Step objects (each has .agent, .input_key, .output_key)
        self.steps = steps or []

    async def _arun(self, initial: Dict[str, Any]):
        artifacts = dict(initial or {})
        for step in self.steps:
            agent = step.agent
            # prepare input for the step
            if isinstance(step.input_key, list):
                in_data = {k: artifacts.get(k) for k in step.input_key}
            else:
                # May be a single key like "user_request" -> we pass its value (not a dict)
                in_data = artifacts.get(step.input_key, initial.get(step.input_key) if initial else None)

            run_fn = getattr(agent, "run", None)
            if run_fn is None:
                raise RuntimeError(f"Agent {agent} has no run() method.")

            # support async and sync run implementations
            if asyncio.iscoroutinefunction(run_fn):
                result = await run_fn(in_data)
            else:
                maybe = run_fn(in_data)
                if asyncio.isawaitable(maybe):
                    result = await maybe
                else:
                    result = maybe

            # if result is StepResult-like, unwrap
            if hasattr(result, "output"):
                artifacts[step.output_key] = result.output
            else:
                artifacts[step.output_key] = result
        return artifacts

    def run(self, initial: Dict[str, Any]):
        # provide sync facade
        try:
            return asyncio.run(self._arun(initial or {}))
        except RuntimeError:
            # fallback if event loop already running
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(self._arun(initial or {}))
            finally:
                loop.close()

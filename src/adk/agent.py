# src/adk/agent.py

class SequentialAgent:
    def __init__(self, steps=None):
        # ذخیره مراحل workflow
        self.steps = steps or []

    # همان async run که قبلا گذاشتیم
    async def _arun(self, initial: dict):
        artifacts = dict(initial)
        for step in self.steps:
            agent = step.agent
            if isinstance(step.input_key, list):
                in_data = {k: artifacts.get(k) for k in step.input_key}
            else:
                in_data = artifacts.get(step.input_key, initial.get(step.input_key))
            run_fn = getattr(agent, "run", None)
            if run_fn is None:
                raise RuntimeError(f"Agent {agent} has no run() method.")
            if asyncio.iscoroutinefunction(run_fn):
                result = await run_fn(in_data)
            else:
                maybe = run_fn(in_data)
                if asyncio.isawaitable(maybe):
                    result = await maybe
                else:
                    result = maybe
            if hasattr(result, "output"):
                artifacts[step.output_key] = result.output
            else:
                artifacts[step.output_key] = result
        return artifacts

    def run(self, initial: dict):
        try:
            return asyncio.run(self._arun(initial))
        except RuntimeError:
            loop = asyncio.new_event_loop()
            return loop.run_until_complete(self._arun(initial))


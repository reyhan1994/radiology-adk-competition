# src/adk/agent.py

class SequentialAgent:
    def __init__(self):
        pass

class FunctionAgent:
    def __init__(self, name, function):
        self.name = name
        self.function = function

class Agent:
    async def run(self, artifacts):
        return {"mock": True}

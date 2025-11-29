# src/adk/step.py

class Step:
    def __init__(self, name, agent, input_key, output_key):
        self.name = name
        self.agent = agent
        self.input_key = input_key
        self.output_key = output_key

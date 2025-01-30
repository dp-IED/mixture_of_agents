# ThoughtLLM.py single class for generating thoughts from user input
# Eventually will use a fine-tuned llama3.1:8b model

import ollama
from 

class ThoughtLLM:
  def __init__(self, model_name: str = "llama3.1:8b"): # replace by a fine-tuned model
    self.model_name = model_name
    self.ollama_client = ollama.Client()

  def generate_thoughts(self, user_input: str) -> str:
    return self.ollama_client.generate(model=self.model_name, prompt=user_input)

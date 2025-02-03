## open halucinations folder 
import os

import deepeval
import ollama 

from deepeval.metrics import (
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric
)

class FineTuner:
  def __init__(self):
    self.llm = ollama.AsyncClient()
    self.metrics = [ContextualRelevancyMetric(), ContextualRecallMetric(), ContextualPrecisionMetric()]
    
  async def process_hallucinations(self, folder_path):
    ## formally this only handles halucinations for the Knowledge Agent, could be expanded to also improve train of thought generation
    # (more efficient thought generation, better inputs more aligned with the user's preferences retrieved from Long-Term Memory)
    query = open(os.path.join(folder_path, "query.txt")).read()
    text = open(os.path.join(folder_path, "text.txt")).read()
    rag = open(os.path.join(folder_path, "rag.txt")).read()
    
    
    system_message = f"""
    You are a prompt engineer for high end RAG models, your query has been hallucinated. 
    
    The user's query was: {query}
    The model's response was: {text}
    The retrieval context was: {rag}
    
    Several metrics are also at your disposal: 
    {self.metrics}
    
    You must generate a new response that is more accurate and relevant to the user's query 
    """
  
    ## give it a second try:
    response = await self.llm.chat(
    model="llama3.1:8b",
    messages=[
      {"role": "system", "content": system_message},
      {"role": "user", "content": query},
      {"role": "assistant", "content": text}
    ]
  )
  
  from deepeval.test_case import LLMTestCase
  test_case = LLMTestCase(
    input=query,
    actual_output=text,
    expected_output="You can stay up to 60 days after completing your degree.",
    retrieval_context=[
        """If you are in the U.S. on an F-1 visa, you are allowed to stay for 60 days after completing
        your degree, unless you have applied for and been approved to participate in OPT."""
    ]
  )
  n = 0
  while os.path.exists("hallucinations"):
    n += 1
    process_hallucinations(os.path.join("hallucinations", f"hallucinations_{n}"))




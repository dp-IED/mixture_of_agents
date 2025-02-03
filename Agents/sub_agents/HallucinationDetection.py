# watch out this might become paid at some point, might increase the local memory on potential searches as well

# https://github.com/open-llm-lab/deepeval

from deepeval.metrics import (
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric
)

contextual_precision = ContextualPrecisionMetric()
contextual_recall = ContextualRecallMetric()
contextual_relevancy = ContextualRelevancyMetric()


from deepeval.test_case import LLMTestCase


class HallucinationDetection:
  def __init__(self):
    pass

  def percentage_hallucination(self, query: str, text: str, rag: str) -> float:
    test_case = LLMTestCase(
      input=query,
      actual_output=text,
      retrieval_context=rag,
    )

    
    print("Score: ", contextual_precision.score)
    print("Reason: ", contextual_precision.reason)
    
    if contextual_precision.score < 0.5:
      ## really bad ones, we train these in the background when the user isn't using the app
      
      import os
      os.makedirs("hallucinations", exist_ok=True)
      with open("hallucinations/query.txt", "w") as f:
        f.write(query)
      with open("hallucinations/text.txt", "w") as f:
        f.write(text)
      with open("hallucinations/rag.txt", "w") as f:
        f.write(rag)




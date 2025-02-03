# Here i put a bunch of bash scripts i want to install to docker compose if it hasn't been installed yet
import os 
import sys
from pathlib import Path

# Add project root to Python path
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

## Initialise thoughtLLM and Agents

from Agents.KnowledgeAgent import KnowledgeAgent
from setup.ThoughtLLM import ThoughtLLM


thought_llm = ThoughtLLM()
knowledge_agent = KnowledgeAgent()

import asyncio

## given a query, the chat method should return an array of thoughts:
## thoughts are tuples of (thought, (action, args)) 
## thoughts are given to final layer which is the agentic loop which runs the actions
## when all actions are complete, the agentic loop pushes the outputs to the final layer which returns the answer
## chat is also passed an array of tools
## this puts the agentic loop in the main file which will help for server/client implementation

agents = [
  KnowledgeAgent
]

while True:  
  thoughts = asyncio.run(thought_llm.chat(input("Enter a query: "), agents)) # think of a good abstraction, .chat 
  for (thought, (action, args)) in thoughts:
    print(thought)


## TODO: 
## [x] Search tool 
## [] Thought Generation (first layer)
## [] Agentic loop (final layer and piecing it together, since agentic loop is thought gen at this stage)
## [] User Interface Experimentation
# ThoughtLLM.py single class for generating thoughts from user input
# Eventually will use a fine-tuned llama3.1:8b model

import ollama
import sys
from pathlib import Path

# Add parent directory to Python path to find Agents module
sys.path.append(str(Path(__file__).parent.parent))

from Agents.KnowledgeAgent import KnowledgeAgent

class ThoughtLLM:
  def __init__(self, model_name: str = "llama3.1:8b", llm = None): # replace by a fine-tuned model
    self.model_name = model_name
    self.llm = llm or ollama.AsyncClient()  # Use AsyncClient by default
    self.knowledge_agent = KnowledgeAgent(llm=self.llm)  # Pass the same client
    self.tools = self.knowledge_agent.tools

  async def generate_thoughts(self, user_input: str):
      
    ## Start without streaming for easier prototyping
    default_system_message = (
        'Act as a chain of thought model.'
        'Your task is to generate ONLY the most obvious next thought an intelligent '
        'human would have before responding. Once you have logically '
        'thought about the user\'s prompt enough times to feel confident generate [thinking complete].'
        'Do not generate the following thought.'
        
        'You have access to the following tools:'
        f' Knowledge Agent: to search the web and the local knowledge base for information. Input is a string (query)'
        
    )
    
    thoughts = [user_input]
    thinking_complete = False
    
    print(f"\nInitial Input: {user_input}\n")
    
    while not thinking_complete:
        # Construct messages with previous thoughts
        messages = [
            {"role": "system", "content": default_system_message},
            {"role": "user", "content": user_input}
        ]
        
        if len(thoughts) > 1:
            context = "\n".join([f"Thought: {thought}" for thought in thoughts[1:]])
            messages.append({"role": "assistant", "content": context})
        
        print("\nContext:")
        print(messages[-1].get("content") if len(messages) > 2 else "No previous thoughts yet")
        
        # Get the next thought using async chat
        response = await self.llm.chat(
            model=self.model_name,
            messages=messages,
            tools=self.tools,
        )
        
        ## TODO: below doesn't work yet
        ## [] thought extraction
        ## [] tool extraction (name and args)
        
        thoughts.append(current_thought)
        print("\nComplete thought:", current_thought)
        thinking_complete = current_thought.lower().endswith("[thinking complete]")
        
        if thinking_complete:
            yield "[END]"  # Signal completion instead of returning

async def chat(messages, thought_process):
    pass

if __name__ == "__main__":
    async def run():
        thought_llm = ThoughtLLM()
        user_input = "What is the capital of France?"
        
        thoughts = []
        async for thought_chunk in thought_llm.generate_thoughts(user_input):
            if thought_chunk == "[END]":
                break
            print(thought_chunk, end='', flush=True)
            thoughts.append(thought_chunk)
    
    import asyncio
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\nExiting...")
        exit(0)
    
import json
import ollama
from ollama import Tool, ChatResponse
import sys
from pathlib import Path

# Add project root to Python path if not already there
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

# Use absolute imports when importing sub-agents
from Agents.sub_agents.web.WebSearch import WebSearch
from Agents.sub_agents.LocalFileSearch import LocalFileSearch
from Agents.sub_agents.RemoteDatabaseSearch import RemoteDatabaseSearch
from Agents.sub_agents.HallucinationDetection import HallucinationDetection


class KnowledgeAgent:
    def __init__(self, llm = ollama.AsyncClient()):
        self.web_search_tool = {
            'type': 'function',
            'function': {
                'name': 'web_search',
                'description': 'Search the web for the user\'s input',
                'parameters': {
                'type': 'object',
                'required': ['query'],
                'properties': {
                    'query': {'type': 'string', 'description': 'The query to search the web for'},
                },
                },
            },
        }
        
        
        self.tools = [
            ollama.Tool(
                name="Knowledge Agent",
                description="Search the web and the local knowledge base for information",
                func=self.search
            )
        ]
        
        self.llm = llm
        self.web_search = WebSearch()
        self.web_search_tool = self.web_search.get_tool()
        self.local_file_search = LocalFileSearch()
        self.remote_database_search = RemoteDatabaseSearch()
      
    async def search(self, user_input: str) -> str:
        """
        Searches the Local File System and Remote Database for the user's input by default.
        If the user's input is not found, searches the Web for the user's input.
        """
        # Search local sources first
        local_file_search_results = self.local_file_search.search(user_input)
        remote_database_search_results = self.remote_database_search.search(user_input)
        
        tagged_results = """
        --- Local File System ---
        {local_file_search_results}
        --- Remote Database ---
        {remote_database_search_results}
        """
        
        prompt = f"""You are a research assistant. Given a user's query and local documents, 
        determine if web search is needed.
        
        Query: {user_input}
        Local documents: {tagged_results}
        
        If local documents are sufficient, return: {{"tool": "none"}}
        If web search is needed, return: {{"tool": "web_search", "query": "<your specific search query>"}}
        
        Example:
        Query: What is the capital of France?
        Local documents: []
        Response: {{"tool": "web_search", "query": "capital city of France"}}
        """
        
        try:
            response = await self.llm.chat(
                model="qwen2.5:14b", 
                format="json", 
                messages=[
                    {"role": "system", "content": prompt}, 
                    {"role": "user", "content": user_input}
                ],
                stream=False
            )
            
            if response.message and response.message.content:
                decision = json.loads(response.message.content)
                if decision.get("tool") == "web_search":
                    query = decision.get("query", user_input)
                    web_results = self.web_search.search(query)
                    # Join the web results if they're a list
                    if isinstance(web_results, list):
                        web_results = ' '.join(web_results)
                    tagged_results += f"\n--- Web Search --- \n{web_results}"
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"Error processing response: {e}")
            
        return tagged_results


async def main():
    knowledge_agent = KnowledgeAgent()
    print(await knowledge_agent.search(input("Enter a query: ")))

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting...")
        exit(0)

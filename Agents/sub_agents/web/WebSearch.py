from .SearxNG import SearxNG

class WebSearch:
    def __init__(self):
        self.searx = SearxNG() # SearxNG is a class that initialises a SearxNG container
    
    def get_tool(self):
        return self.searx.get_tool()
    
    def search(self, query: str) -> str:
        fun = self.searx.search
        return fun(query)
    
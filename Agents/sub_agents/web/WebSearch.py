from .SearxNG import SearxNG
import atexit

class WebSearch:
    def __init__(self):
        self.searx = SearxNG() # SearxNG is a class that initialises a SearxNG container
        # Register cleanup with atexit as backup
        atexit.register(self.cleanup)
    
    def get_tool(self):
        return self.searx.get_tool()
    
    def search(self, query: str) -> str:
        fun = self.searx.search
        return fun(query)
    
    def cleanup(self):
        if hasattr(self, 'searx'):
            self.searx.cleanup()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
    
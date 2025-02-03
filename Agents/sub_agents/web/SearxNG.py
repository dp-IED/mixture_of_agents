## this should be initialized at the start of the program, and then used to search the web for information

import os
import time
import signal
import requests
import subprocess
import atexit
from langchain_community.utilities import SearxSearchWrapper


## SearxNG (meta-search locally in docker)
class SearxNG:
    _instance = None  # Singleton instance
    
    def __init__(self, port: int = 8080, host: str = "localhost", max_retries: int = 5):
        if SearxNG._instance is not None:
            return
            
        SearxNG._instance = self
        self.container_id = None
        
        # Register cleanup handlers
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Get the config directory path
        config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "searxng-config")
        os.makedirs(config_dir, exist_ok=True)
        
        try:
            existing_container = subprocess.check_output(
                ["docker", "ps", "-a", "--filter", "ancestor=searxng/searxng", "--format", "{{.ID}}"]
            ).decode().strip()
            
            if existing_container:
                self.container_id = existing_container
                container_status = subprocess.check_output(
                    ["docker", "inspect", "-f", "{{.State.Running}}", existing_container]
                ).decode().strip()
                
                if container_status == "true":
                    print(f"Found running SearxNG container: {existing_container}")
                else:
                    print(f"Starting existing container: {existing_container}")
                    subprocess.run(["docker", "start", existing_container])
            else:
                # No existing container, create new one
                if not self.is_port_in_use(port):
                    docker_cmd = [
                        "docker", "run", "-d",
                        "-v", f"{config_dir}:/etc/searxng",
                        "-p", f"{port}:{port}",
                        "searxng/searxng"
                    ]
                    self.container_id = subprocess.check_output(docker_cmd).decode().strip()
                    print(f"Created new SearxNG container: {self.container_id}")
        
        except subprocess.CalledProcessError as e:
            print(f"Docker command failed: {e}")
            self.cleanup()
            raise
        
        # Initialize the client
        self.searx_url = f"http://{host}:{port}"
        self.wrapper = SearxSearchWrapper(searx_host=self.searx_url)
        print(f"Connecting to SearxNG at {self.searx_url}")
        
        # Wait for service to be ready
        self._wait_for_service(max_retries)

    def _wait_for_service(self, max_retries):
        retries = 0
        while retries < max_retries:
            try:
                response = requests.get(f"{self.searx_url}/search")
                if response.status_code in [200, 404]:
                    print(f"SearxNG service is ready at {self.searx_url}")
                    return
            except requests.exceptions.RequestException as e:
                print(f"Waiting for SearxNG service (attempt {retries + 1}/{max_retries}): {e}")
                time.sleep(2)
                retries += 1
        
        raise RuntimeError(f"SearxNG service failed to start after {max_retries} attempts")

    def _signal_handler(self, signum, frame):
        print("\nReceived signal to shutdown...")
        self.cleanup()
        exit(0)

    def cleanup(self):
        if self.container_id:
            try:
                print(f"Stopping SearxNG container: {self.container_id}")
                subprocess.run(["docker", "stop", self.container_id], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Failed to stop container: {e}")
            finally:
                self.container_id = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def get_tool(self):
        if not hasattr(self, 'wrapper'):
            raise RuntimeError("SearxNG service not properly initialised")
        return self.wrapper.run

    def search(self, query: str) -> str:
        if not hasattr(self, 'wrapper'):
            raise RuntimeError("SearxNG service not properly initialised")
        return self.wrapper.run(query)

    def is_port_in_use(self, port: int) -> bool:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

if __name__ == "__main__":
    searx = SearxNG()
    print(searx.search("What is the capital of France?"))
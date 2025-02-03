## this should be initialized at the start of the program, and then used to search the web for information

import os
import time
import requests
import subprocess
from langchain_community.utilities import SearxSearchWrapper


## SearxNG (meta-search locally in docker)
class SearxNG:
    def __init__(self, port: int = 8080, host: str = "localhost", max_retries: int = 5):
        # Get the config directory path
        config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "searxng-config")
        os.makedirs(config_dir, exist_ok=True)
        
        # Check for existing container
        try:
            existing_container = subprocess.check_output(
                ["docker", "ps", "-a", "--filter", "ancestor=searxng/searxng", "--format", "{{.ID}}"]
            ).decode().strip()
            
            if existing_container:
                # Check if container is running
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
                    container_id = subprocess.check_output(docker_cmd).decode().strip()
                    print(f"Created new SearxNG container: {container_id}")
        
        except subprocess.CalledProcessError as e:
            print(f"Docker command failed: {e}")
            raise
        
        # Initialize the client
        self.searx_url = f"http://{host}:{port}"
        self.wrapper = SearxSearchWrapper(searx_host=self.searx_url)
        print(f"Connecting to SearxNG at {self.searx_url}")
        
        # Wait for service to be ready
        retries = 0
        while retries < max_retries:
            try:
                response = requests.get(f"{self.searx_url}/search")
                if response.status_code in [200, 404]:
                    print(f"SearxNG service is ready at {self.searx_url}")
                    break
            except requests.exceptions.RequestException as e:
                print(f"Waiting for SearxNG service (attempt {retries + 1}/{max_retries}): {e}")
                time.sleep(2)
                retries += 1
        
        if retries == max_retries:
            raise RuntimeError(f"SearxNG service failed to start after {max_retries} attempts")

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

    def __del__(self):
        # Optionally stop the container when the object is destroyed
        try:
            container = subprocess.check_output(
                ["docker", "ps", "-q", "--filter", "ancestor=searxng/searxng"]
            ).decode().strip()
            if container:
                subprocess.run(["docker", "stop", container])
        except:
            pass

    def stop(self):
        try:
            container = subprocess.check_output(
                ["docker", "ps", "-q", "--filter", "ancestor=searxng/searxng"]
            ).decode().strip()
            if container:
                subprocess.run(["docker", "stop", container])
        except subprocess.CalledProcessError as e:
            print(f"Failed to stop container: {e}")

if __name__ == "__main__":
    searx = SearxNG()
    print(searx.search("What is the capital of France?"))
from typing import Union
from openai import OpenAI
from pydantic import Field, BaseModel
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseTool, BaseToolConfig
from atomic_agents.lib.components.agent_memory import Message
import json
import requests


class WebSearchInputSchema(BaseIOSchema):
    """The Input Schema for the Web Search Tool"""

    prompt: str = Field(
        ...,
        description="A question or prompt which the Agent will try to answer using internet search",
    )
    searchMethod: str = Field(
        default="webSearch",
        description="The methods supported by the Tool are 'webSearch', 'academicSearch', 'writingAssistant', 'wolframAlphaSearch', 'youtubeSearch', 'redditSearch'. By default only webSearch is selected.",
    )
    optimizationMode: str = Field(
        description="Prioritize speed or take substantially more time for research (can have a value of 'speed' or 'balanced'). By default speed is selected",
        default="speed",
    )


class WebSearchOutputSchema(BaseIOSchema):
    """The Output Schema for the Web Search Tool"""

    answer: str = Field(..., description="The output of the Perplexica Web Search")
    documents: list[dict] = Field(
        ..., description="List of documents with page content and metadata"
    )  # these could be summrized, embedded and stored in vector db during cleanupfor long term memory


class WebSearchConfig(BaseToolConfig):
    """The Perplexica Config"""

    host: str = Field(
        description="The url to the Perplexica API",
        default="http://localhost:3001/api/search",
    )
    model: str = Field(description="The LLM used by Perplexcia", default="qwen2.5:7b")
    embedding_model: str = Field(
        description="The embedding model used by Perplexica",
        default="nomic-embed-text:latest",
    )


class WebSearchTool(BaseTool):
    """Searches the web using Perplexica"""

    name = "WebSearch"
    input_schema = WebSearchInputSchema
    output_schema = WebSearchOutputSchema
    provider = "ollama"

    def __init__(
        self,
        messages: list[Message],
        config: BaseToolConfig = WebSearchConfig(),
    ):
        super().__init__(config)
        self.host = config.host
        self.model = config.model
        self.embedding_model = config.embedding_model
        self.messages = [
            [message["role"], message["content"]] for message in messages
        ]  # Convert to [[role, content]]

    def run(self, params: WebSearchInputSchema) -> WebSearchOutputSchema:
        payload = {
            "chatModel": {"provider": "ollama", "model": self.model},
            "embeddingModel": {"provider": "ollama", "model": self.embedding_model},
            "optimizationMode": params.optimizationMode,
            "focusMode": params.searchMethod,
            "query": params.prompt,
            "history": self.messages,
        }

        json_ouput = requests.post(url=self.host, json=payload).json()
        return WebSearchOutputSchema(
            answer=json_ouput["message"], documents=json_ouput["sources"]
        )

from typing import Union, Literal
from atomic_agents.agents.base_agent import (
    BaseAgent,
    BaseAgentConfig,
    BaseAgentInputSchema,
    BaseIOSchema,
)
from atomic_agents.lib.base.base_tool import BaseTool
from atomic_agents.lib.components.agent_memory import AgentMemory
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from backend.Agents.PerplexityLocal import (
    WebSearchInputSchema,
    WebSearchOutputSchema,
    WebSearchTool,
    WebSearchConfig,
)
from backend.Agents.KnowledgeBase import KnowledgeBase, KnowledgeBaseInputSchema, KnowledgeBaseOutputSchema
import instructor
from openai import OpenAI as OllamaClient
from pydantic import BaseModel, Field


class OrchestratorInputSchema(BaseIOSchema):
    """Input schema for the Orchestrator Agent. Contains the user's message to be processed."""

    chat_message: str = Field(
        ..., description="The user's input message to be analyzed and responded to."
    )


class OrchestratorOutputSchema(BaseIOSchema):
    """Combined output schema for the Orchestrator Agent. Contains the tool to use and its parameters."""

    reasoning: str = Field(
        ...,
        description="Your explanation to the user for using this tool. You should tie this into the previous tool use and the global context of the task.",
    )
    tool: Literal["WebSearch"] = Field(
        ..., description="The tool to use. Must be one of the available tools."
    )
    tool_parameters: WebSearchInputSchema = Field(
        ..., description="The parameters for the selected tool"
    )
    done: bool = Field(
        ...,
        description="Whether the Agent is done and has returned the final answer in the reasoning field",
    )


class Orchestrator:
    input_schema = OrchestratorInputSchema
    output_schema = OrchestratorOutputSchema

    def __init__(
        self,
        model="qwen2.5:7b",
    ):
        self.client = instructor.from_openai(
            OllamaClient(base_url="http://127.0.0.1:11434/v1", api_key="ollama"),
            mode=instructor.Mode.JSON,
        )
        self.model = model
        self.memory = AgentMemory()
        self.tool_names = ["WebSearch", "KnowledgeBase"]
        self.system_prompt_gen = SystemPromptGenerator(
            background=[
                "You are a tool calling Agent that helps answer questions.",
                "Your task is to use tools to complete the user's objective.",
                f"You have access to the following tools: {', '.join(self.tool_names)}",
            ],
            steps=[
                "Break down the user's task into tool calls",
                "Explain your reasoning at each step",
            ],
            output_instructions=[
                "You should return using JSON only and following the given JSON Schema",
                "Be original and creative, consider thoroughly the subjects during each step to bring original, underrepresented opinions and points of view to the user",
                "If you have any questions for the user, follow the JSON schema to get answers or help from the user to accomplish your task",
                f"The tool field must be one of: {', '.join(self.tool_names)}",
            ],
        )
        self.agent = BaseAgent(
            config=BaseAgentConfig(
                client=self.client,
                memory=self.memory,
                model=self.model,
                system_prompt_generator=self.system_prompt_gen,
                input_schema=self.input_schema,
                output_schema=self.output_schema,
            )
        )

    def execute_tool(
        self, tool_name: str, params: Union[WebSearchInputSchema, KnowledgeBaseInputSchema]
    ) -> Union[WebSearchOutputSchema, KnowledgeBaseOutputSchema]:
        if tool_name == "WebSearch":
            tool = WebSearchTool(
                messages=self.agent.memory.get_history(), config=WebSearchConfig()
            )
            print(f"\n=== Running {tool_name} ===")
            print(f"Parameters: {params}")
            output = tool.run(params=params)
            print(f"\n=== {tool_name} Results ===")
            print(f"Main Answer: {output.answer}")
            print(f"Sources: {output.documents}")
            print("=" * 50)
            return output
        elif tool_name == "KnowledgeBase":
            tool = KnowledgeBase()
            print(f"\n=== Running {tool_name} ===")
            print(f"Parameters: {params}")
            output = tool.run(params=params)
            print(f"\n=== {tool_name} Results ===")
            print(f"Main Answer: {output.answer}")
            print(f"Sources: {output.documents}")
            print("=" * 50)
            

    def __call__(self, query: str, max_iterations: int = 5) -> OrchestratorOutputSchema:
        """
        Execute the agent's task with the given query, running tools and continuing until done.
        """
        current_iteration = 0
        print(f"\n🤖 Initial Query: {query}\n")
        response = self.agent.run(BaseAgentInputSchema(chat_message=query))
        print(f"🤔 Agent Reasoning: {response.reasoning}\n")

        while not response.done and current_iteration < max_iterations:
            if response.tool and response.tool_parameters:
                try:
                    print(f"\n📎 Iteration {current_iteration + 1}")
                    action_result = self.execute_tool(
                        tool_name=response.tool, params=response.tool_parameters
                    )

                    # Get next action from agent
                    next_prompt = f"Tool {response.tool} returned: {action_result}"
                    response = self.agent.run(
                        BaseAgentInputSchema(chat_message=next_prompt)
                    )
                    print(f"\n🤔 Agent Reasoning: {response.reasoning}\n")

                except Exception as e:
                    error_message = f"❌ Error executing tool {response.tool}: {str(e)}"
                    print(error_message)
                    response = self.agent.run(
                        BaseAgentInputSchema(chat_message=error_message)
                    )
                    print(f"\n🤔 Agent Reasoning: {response.reasoning}\n")

            current_iteration += 1

        if current_iteration >= max_iterations:
            print(f"\n⚠️ Warning: Reached maximum iterations ({max_iterations})")
            return self.agent.memory.get_history()

        print("\n✅ Task completed!")
        # add messages to evaluation dataset
        return response


if __name__ == "__main__":
    ag = Orchestrator()
    r = ag("Hello Agent, can you tell me about setting up Hyprland on Fedora Linux?")
    print("\n🔍 Final Response:")
    print(r)

# Mixture of Agents: AI Workbench Application for Public Policy Research and Execution (SIMpol)

![SIMpol](./logo.png)

## Pipeline Workflow

- Thoughts are generated from the user's question using a lightweight local llama3.1:8b model. *(The model is finetuned to both write thoughts to aid the final response generation but also to create prompts according to these thoughts.)* 
- The stream of text thoughts is passed to the user, and the prompts are passed to the relevant Agents.
- Agents are usually ran on a capable local model which supports tool calling (Qwen2.5:14b) or a specialised local model (Qwen2.5 Coder:14b / 32b for programming).

## User Experience

First the user's question is passed to the LLM to generate thoughts. (Inspiration: [An AI generates text thoughts](https://www.youtube.com/watch?v=rmEmsZmlvNo&t=969s))

The thoughts are comprised of a text response and a set of prompts which are passed to the Agents.

While the Agents work on the prompts, the user is streamed the text response which gives the user a sense of progress. The user can also see the Agents working on the prompts.

This is just the start of the process, the Agents return their results which are progressively displayed to the user as artifacts. The requests on specific artifacts are stored in memory which can be accessed by the Agent only or by other agents or the base LLM on-request.

Then comes the itterative process, where the user can control each Agent output with further prompts. The user can refine the current artifact, go back to the previous step or add an agent to the deliberative process either with prompts suggested by the thinking LLM or a new question.

__Starter Agents are responsible for different tasks, such as:__

-  Calculator related tasks (most maths, analysis, stats, formulas evaluated through python libraries)
-  Data Visualization (Text, File System, Video, Images, Audio, Charts, Tables)
- Information Retrieval (Web, Files, SQL Databases, other databases might require a Connector Agent)
- Code Generation (access to an appropriate code interpreter, itterative loop for code generation, can also be called by other Agents)

![[Architecture](https://excalidraw.com/#json=Rd1qAyqYdpyiXuEGUoP5M,o2PKOs3xVkKxS6gtX5VFzw)](./system_architecture.excalidraw.png)

## Agent Expansion

These Agents can be expanded with custom Agents that are responsible for specific skillsets.

#### Let's say you work in city planning. You would create an Agent solely responsible for rendering maps. 

It would know the challenges of rendering maps (strategies for high polygon count), throw the weeks of using it you would have taught it the main features of your city it and would be able to call the appropriate Agents to get complementary data.

## Project Difficulty Table

| Task | Difficulty | Time |
| --- | --- | --- |
| Fine-tune Llama 3.1 (8B) for thought generation | 8/10 | 20h |
| Performant Model Orchestration | 10/10 | 35h |
| Shared / On-request Memory | 10/10 | 20h |
| Calculator Agent | 4/10 | 8h |
| Data Visualisation Agent | 7/10 | 12h |
| Search Agent | 8/10 | 18h (lots of different search methods) |
| Code Generation Agent | 9/10 | 16h |
| User Interface | 10/10 | 10h (Research and user testing mostly) |
|Total| | 139h |

### Course of Action:

- Implement the Thought_LLM class for generating thoughts and prompts
- Develop the Calculator Agent
- Develop necessary parts of the Data Visualisation Agent
- Try it out with Maths questions
- **Expand with a Search Agent**
- **Expand User Interface to make it the best research board ever**

### Note: User Interface Development
- Implement streaming interface for thoughts
- Create visualization area for agent outputs
- Add interactive controls for:
  - Agent selection
  - Prompt refinement
  - Result iteration
  - Work session summary

## Next Steps
After completing the basic implementation:
- Add more specialized agents
- Implement advanced caching for model inference
- Create agent templates for custom domain-specific agents

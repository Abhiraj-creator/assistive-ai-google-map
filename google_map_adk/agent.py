import os
from pathlib import Path
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from . import prompt

# Load .env from the project root (one level up from this package)
_root_env = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_root_env, override=False)

# Retrieve API keys from environment variables
google_maps_api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
groq_api_key = os.environ.get("GROQ_API_KEY")

if not google_maps_api_key:
    print("WARNING: GOOGLE_MAPS_API_KEY is not set.")

if not groq_api_key:
    print("WARNING: GROQ_API_KEY is not set.")
else:
    # LiteLlm needs GROQ_API_KEY in the environment for groq/ prefix models
    os.environ["GROQ_API_KEY"] = groq_api_key

# ADK v2.13: Use LiteLlm with the groq/ model prefix.
# LiteLlm routes "groq/llama-3.3-70b-versatile" to Groq's API automatically.
llm = LiteLlm(model="groq/llama-3.3-70b-versatile")

root_agent = LlmAgent(
    model=llm,
    name="google_map_adk",
    instruction=prompt.instruction,
    tools=[
        MCPToolset(
            connection_params=StdioServerParameters(
                command="npx",
                args=[
                    "-y",
                    "@modelcontextprotocol/server-google-maps",
                ],
                # Pass the Google Maps API key to the MCP server process
                env={
                    "GOOGLE_MAPS_API_KEY": google_maps_api_key or "",
                },
            ),
        ),
    ],
)

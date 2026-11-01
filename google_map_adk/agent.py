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

# LiteLLM needs the Groq provider prefix. Keep the model configurable so a
# retired Groq model does not remain hardcoded in the agent.
configured_model = (
    os.environ.get("GROQ_MODEL")
    or os.environ.get("GOOGLE_ADK_MODEL")
    or "openai/gpt-oss-120b"
)
llm_model = configured_model if configured_model.startswith("groq/") else f"groq/{configured_model}"
# GPT-OSS supports explicit reasoning effort on Groq. Do not pass the
# unsupported history-filter options through LiteLLM.


class GroqLiteLlm(LiteLlm):
    """Keep ADK's internal reasoning history out of Groq chat requests."""

    async def generate_content_async(self, llm_request, stream=False):
        sanitized_request = llm_request.model_copy(deep=False)
        sanitized_request.contents = [
            content.model_copy(
                update={
                    "parts": [
                        part
                        for part in (content.parts or [])
                        if not (
                            content.role in ("model", "assistant")
                            and getattr(part, "thought", False)
                        )
                    ]
                }
            )
            for content in llm_request.contents
        ]
        async for response in super().generate_content_async(
            sanitized_request, stream=stream
        ):
            yield response


llm = GroqLiteLlm(model=llm_model, reasoning_effort="low")
5
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

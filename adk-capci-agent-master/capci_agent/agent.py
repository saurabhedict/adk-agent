import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StreamableHTTPConnectionParams,
)


load_dotenv()

CAPCI_API_KEY = os.getenv("CAPCI_API_KEY")
CAPCI_MCP_URL = os.getenv(
    "CAPCI_MCP_URL",
    "https://mcp.capci.app/mcp",
)

if not CAPCI_API_KEY:
    raise RuntimeError(
        "CAPCI_API_KEY is missing from the .env file."
    )

if CAPCI_API_KEY.startswith("capci_REPLACE"):
    raise RuntimeError(
        "Replace the CAPCI_API_KEY placeholder with your actual CapCI key."
    )


capci_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=CAPCI_MCP_URL,
        headers={
            "x-api-key": CAPCI_API_KEY,
            # This User-Agent does double duty: it identifies the client as ADK in
            # Capci's analytics AND tells the Capci MCP server to skip the inline
            # image block. ADK's dev UI renders the markdown image from previewUrl
            # (in the model's text), not the tool-result block — so the server
            # auto-suppresses the block for a "google-adk"/"capci-adk" User-Agent,
            # avoiding ~50K tokens/image of Gemini context waste. No x-capci-inline
            # header needed (it would still override if you set one).
            "User-Agent": "capci-adk-agent/1.0 (google-adk)",
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
        },
    ),
)


root_agent = Agent(
    name="capci_agent",
    # gemini-2.5-pro: reliable native tool-calling. gemini-2.5-flash tends to LOOP
    # (fire a second create_diagram on its own) which stalls the run — that was the
    # "response never comes back", not the image size.
    model="gemini-2.5-pro",
    description=(
        "A simple ADK agent connected to the CapCI MCP server."
    ),
    instruction="""
You are a CapCI assistant.

Use the available CapCI MCP tools whenever the user asks you to
create or edit visual content such as posts, diagrams, carousels,
charts, animations, or branded assets.

For this test:
1. Always use an MCP tool when the user explicitly asks you to test CapCI.
2. Do not claim that content was created unless the MCP tool succeeds.
3. Report any authentication, validation, or MCP connection errors clearly.
4. Keep test requests simple.

When a tool returns an image, display it inline as a markdown image on its own
line using the exact previewUrl from the tool result (a right-sized inline copy),
then a download link below it. Use ONLY the URLs the tool returned verbatim —
never modify or append to them:
    ![<title>](<previewUrl>)
    [Download](<downloadUrl>)
""",
    tools=[capci_toolset],
)
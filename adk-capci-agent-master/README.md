# Google ADK + MCP Agent — Generate Diagrams from a Prompt (Text-to-Diagram)

> A minimal, **runnable Google ADK agent** that connects to an **MCP server** and
> generates architecture diagrams, sequence/ER/class diagrams, animated diagrams,
> and branded posts — from a plain-text prompt. The smallest complete example of
> **ADK + MCP tools** over Streamable HTTP with header auth. Clone, add a key, run.

**Keywords:** google adk · adk mcp · adk mcp server · adk agent example ·
adk tutorial · mcp tools python · model context protocol · agentic ai ·
gemini adk agent · text to diagram · ai diagram generator · adk streamable http

Powered by the [Capci MCP server](https://github.com/vishal-bulbule/capci-mcp).
Uses [Google ADK](https://google.github.io/adk-docs/) for the agent and Gemini as
the reasoning model; Capci is a black-box tool the agent calls.

---

## What this is

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io) lets a Google
ADK agent call external capabilities as native tools. This repo wires ADK's
`McpToolset` to Capci's hosted MCP server, so one agent can, from a prompt:

- **Generate diagrams** — architecture, flowchart, sequence, class, ER, mindmap,
  Gantt — and refine them by id.
- **Animate a diagram** into a reveal GIF.
- **Generate branded social/marketing posts** and data charts.
- **Apply a brand** (colors, logo) once and have every output inherit it.

It's a working reference for three things developers search for constantly:
**how to connect an MCP server to Google ADK**, **how to pass auth headers to a
remote MCP server**, and **how to return images from an MCP tool to a Gemini
agent without blowing the token limit**.

## Architecture

```
You ──▶ Google ADK agent (Gemini)  ──MCP over Streamable HTTP──▶  Capci MCP server
              │                        (x-api-key + x-capci-inline)          │
              └── picks create_diagram / refine_diagram / animate_diagram     └─▶ diagram / post image
```

## Quick start

```bash
# 1. Get a Capci API key at https://capci.app (free tier available).

# 2. Install + configure
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
#    → set CAPCI_API_KEY, and your Gemini credentials (AI Studio key or Vertex project)

# 3. Run
adk web                    # chat UI at http://localhost:8000 → pick "capci_agent"
# or headless:
adk run capci_agent
```

## The agent (how ADK connects to MCP)

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

capci_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://mcp.capci.app/mcp",
        headers={
            "x-api-key": CAPCI_API_KEY,
            # Identifies the client as ADK. The Capci server sees this and returns a
            # URL preview instead of a full-res inline block — which ADK can't render
            # (it shows the model's markdown image), and which Gemini would otherwise
            # re-ingest as text and blow past its token limit. No extra header needed.
            "User-Agent": "capci-adk-agent/1.0 (google-adk)",
        },
    ),
)

root_agent = Agent(
    model="gemini-2.5-pro",   # reliable native tool-calling (flash tends to loop / emit code-style calls)
    name="capci_agent",
    instruction=(
        "After a tool returns an image, display it as a markdown image using "
        "the previewUrl (a right-sized inline copy), then a [Download](downloadUrl) link below it."
    ),
    tools=[capci_toolset],
)
```

See [`capci_agent/agent.py`](capci_agent/agent.py) for the full agent.

## Try these prompts

- `Create an architecture diagram of a secure Google Cloud landing zone.`
- `Create an architecture diagram: user → API → database with a cache.`
- `Make it dark and freeform.` — refines the same diagram by id
- `Animate the request flow as a GIF.`
- `Now a LinkedIn post announcing it, on brand.`

## Layout

```
adk-capci-agent/
├── capci_agent/
│   ├── __init__.py       # exposes the agent package to `adk`
│   └── agent.py          # root_agent = Agent + Capci McpToolset
├── .env.example          # copy → .env and fill in
├── requirements.txt
└── README.md
```

## Troubleshooting

**`400 INVALID_ARGUMENT: input token count exceeds the maximum`** — the tool
returned a full-res base64 image and Gemini re-ingested it as text. The server
skips that inline block automatically when it sees the ADK `User-Agent` (shown
above), serving a URL preview instead — make sure that header is set. To force it
on any client, send `x-capci-inline: 0` (no block, URL only).

**`UNEXPECTED_TOOL_CALL: print(agent.create_diagram(...))`** — the model wrote the
tool call as code instead of a real function call. This is a `gemini-2.5-flash`
thinking behavior; switch `model` to `gemini-2.5-pro`, and keep the instruction
free of the words "code" / "print" / "tool_code".

**`Failed to create MCP session`** — the agent can't reach the MCP server. Check
`CAPCI_MCP_URL` (default `https://mcp.capci.app/mcp`) is reachable and your
`x-api-key` is valid.

**The image doesn't render in the ADK dev UI** — some ADK UI builds don't follow
the image URL's redirect. The **Download link always works**, and the image
renders inline in **Claude Code** and real apps. The `preview` header ensures the
inline block is small enough to render where the UI supports it.

## FAQ

**How do I connect an MCP server to Google ADK?** Use `McpToolset` with
`StreamableHTTPConnectionParams`, pass the server URL and any auth headers, and
add the toolset to your `Agent`'s `tools`. Full example above.

**How do I pass an API key / custom headers to a remote MCP server in ADK?** Put
them in the `headers` dict of `StreamableHTTPConnectionParams` — they ride on
every request.

**Which Gemini model should I use for ADK tool-calling?** `gemini-2.5-flash` is
fast and works; `gemini-2.5-pro` is more reliable if you see code-style tool
calls.

**Does this need a local server?** No — it points at the hosted
`mcp.capci.app`. There's nothing to run yourself.

## More

- **[Capci MCP server](https://github.com/vishal-bulbule/capci-mcp)** — per-host setup (Claude, VS Code, Antigravity, Gemini CLI) + the `x-capci-inline` header reference
- **[Text-to-diagram examples](https://github.com/vishal-bulbule/text-to-diagram-examples)** — prompt → diagram gallery
- **[AI social post examples](https://github.com/vishal-bulbule/ai-social-post-examples)** — LinkedIn & animated posts
- **[capci.app](https://capci.app)** — try it in the browser · **[docs](https://capci.app/docs/mcp)**

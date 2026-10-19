"""MCP server exposing the interview catalog, coach and Architecture Review as tools.

Run:   python mcp_server/server.py            (stdio, for Claude Desktop / Claude Code)
       python mcp_server/server.py --http     (streamable HTTP on port 8765)

Works with MCP Python SDK 2.x (MCPServer) and 1.x (FastMCP).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from antipatterns.tools import TOOLS  # noqa: E402

try:  # MCP Python SDK 2.x
    from mcp.server.mcpserver import MCPServer as Server
except ImportError:  # MCP Python SDK 1.x
    from mcp.server.fastmcp import FastMCP as Server

INSTRUCTIONS = """\
Agentic AI interview coach for Telco BSS and FinTech, plus Architecture Review.

Interview mode: call next_question, present the setup and question, wait for the user's
answer, then call grading_rubric, judge each of the 5 criteria true/false, give feedback
with the reference fix and interview line, and call record_attempt.

Architecture Review mode: read architecture_spec_guide, write a spec from the user's
scenario (look at get_reference_architecture('telco-sim-swap-agent') for an example),
check it with check_architecture_spec, then call review_architecture and present the
numbered failure points, fixes and diagrams.
"""

mcp = Server("agentic-ai-interview-prep", instructions=INSTRUCTIONS)

for t in TOOLS:
    mcp.add_tool(t["fn"], name=t["name"], description=t["description"])


def main() -> None:
    if "--http" in sys.argv:
        mcp.run(transport="streamable-http")
    else:
        mcp.run()


if __name__ == "__main__":
    main()

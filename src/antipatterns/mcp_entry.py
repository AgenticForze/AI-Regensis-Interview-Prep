"""Console entry point for the MCP server (aap-mcp)."""
import runpy
from pathlib import Path


def main() -> None:
    runpy.run_path(str(Path(__file__).resolve().parents[2] / "mcp_server" / "server.py"), run_name="__main__")

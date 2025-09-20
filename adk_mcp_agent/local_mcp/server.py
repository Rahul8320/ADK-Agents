import asyncio
import json
import os
import logging

import mcp.server.stdio

# ADK Tool Imports
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.mcp_tool.conversion_utils import adk_to_mcp_tool_type

# MCP Server Imports
from mcp import types as mcp_types
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions

from db import (
    delete_data,
    get_table_schema,
    insert_data,
    list_db_tables,
    query_db_table,
)

# Logging setup
LOG_FILE_PATH: str = os.path.join(os.path.dirname(__file__), "mcp_server.log")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE_PATH, mode="w")],
)

# MCP server setup
logging.info("Creating MCP server instance for SQLite DB...")
app = Server("sqlite-db-mcp-server")

# Warp database utility functions as ADK Function Tools
ADK_DB_TOOLS = {
    "list_db_tables": FunctionTool(func=list_db_tables),
    "get_table_schema": FunctionTool(func=get_table_schema),
    "query_db_table": FunctionTool(func=query_db_table),
    "insert_data": FunctionTool(func=insert_data),
    "delete_data": FunctionTool(func=delete_data),
}


@app.list_tools()
async def list_mcp_tools() -> list[mcp_types.Tool]:
    """MCP handler to list tools this server exposes."""

    logging.info("MCP Server: Received list_tools request.")
    mcp_tools_list = []

    for tool_name, adk_tool_instance in ADK_DB_TOOLS.items():
        if not adk_tool_instance.name:
            adk_tool_instance.name = tool_name

        mcp_tool_schema = adk_to_mcp_tool_type(adk_tool_instance)
        logging.info(
            f"MCP Server: Advertising tool: {mcp_tool_schema.name}, InputSchema: {mcp_tool_schema.inputSchema}"
        )
        mcp_tools_list.append(mcp_tool_schema)

    return mcp_tools_list


@app.call_tool()
async def call_mcp_tool(name: str, arguments: dict) -> list[mcp_types.TextContent]:
    """MCP handler to execute a tool call requested by an MCP client."""

    logging.info(
        f"MCP Server: Received call_tool request for '{name}' with args: {arguments}"
    )

    if name in ADK_DB_TOOLS:
        adk_tool_instance = ADK_DB_TOOLS[name]
        try:
            adk_tool_response = await adk_tool_instance.run_async(
                args=arguments,
                tool_context=None,  # type: ignore
            )
            logging.info(
                f"MCP Server: ADK tool '{name}' executed. Response: {adk_tool_response}"
            )
            response_text = json.dumps(adk_tool_response, indent=2)
            return [mcp_types.TextContent(type="text", text=response_text)]

        except Exception as e:
            logging.error(
                f"MCP Server: Error executing ADK tool '{name}': {e}", exc_info=True
            )
            error_payload = {
                "success": False,
                "message": f"Failed to execute tool '{name}': {str(e)}",
            }
            error_text = json.dumps(error_payload)
            return [mcp_types.TextContent(type="text", text=error_text)]
    else:
        logging.warning(f"MCP Server: Tool '{name}' not found/exposed by this server.")
        error_payload = {
            "success": False,
            "message": f"Tool '{name}' not implemented by this server.",
        }
        error_text = json.dumps(error_payload)
        return [mcp_types.TextContent(type="text", text=error_text)]


# MCP Server Runner
async def run_mcp_stdio_server():
    """Runs the MCP server, listening for connections over standard input/output."""

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logging.info("MCP Stdio Server: Starting handshake with client...")
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=app.name,
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
        logging.info("MCP Stdio Server: Run loop finished or client disconnected.")


if __name__ == "__main__":
    logging.info("Launching SQLite DB MCP Server via stdio...")
    try:
        asyncio.run(run_mcp_stdio_server())
    except KeyboardInterrupt:
        logging.info("\nMCP Server (stdio) stopped by user.")
    except Exception as e:
        logging.error(
            f"MCP Server (stdio) encountered an unhandled error: {e}", exc_info=True
        )
    finally:
        logging.info("MCP Server (stdio) process exiting.")

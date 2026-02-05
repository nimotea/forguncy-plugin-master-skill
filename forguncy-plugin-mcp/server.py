import argparse
from mcp.server.fastmcp import FastMCP
from tools import docs, templates, project, utils

# Initialize the MCP server
mcp = FastMCP("forguncy_plugin_mcp")

# Register tools from modules
docs.register(mcp)
templates.register(mcp)
project.register(mcp)
utils.register(mcp)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Forguncy Plugin MCP Server")
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse"], help="Transport protocol to use (stdio or sse)")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on for SSE transport")
    parser.add_argument("--host", default="0.0.0.0", help="Host to listen on for SSE transport")
    
    args = parser.parse_args()
    
    if args.transport == "sse":
        print(f"Starting SSE server on {args.host}:{args.port}...")
        mcp.settings.host = args.host
        mcp.settings.port = args.port
        
        # Disable DNS rebinding protection to allow external access
        try:
            from mcp.server.transport_security import TransportSecuritySettings
            mcp.settings.transport_security = TransportSecuritySettings(enable_dns_rebinding_protection=False)
            print("DNS rebinding protection disabled for external access.")
        except ImportError:
            print("Warning: Could not import TransportSecuritySettings. External access might be blocked.")
            
        # Note: FastMCP default run_sse_async uses Starlette but doesn't expose CORS easily.
        # If CORS is needed for browser access, we might need to proxy or use a different runner.
        # However, for now, we stick to standard FastMCP SSE.
        mcp.run(transport="sse")
    else:
        mcp.run()

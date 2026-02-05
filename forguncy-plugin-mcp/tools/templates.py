from mcp.server.fastmcp import FastMCP
from pydantic import Field
from config import TEMPLATES_DIR, ICONS_DIR, ensure_base_dir

def register(mcp: FastMCP):
    @mcp.tool(
        name="list_templates",
        annotations={
            "title": "List Templates",
            "readOnlyHint": True,
            "description": "Lists all available code templates."
        }
    )
    def list_templates() -> str:
        """Lists all available code templates."""
        ensure_base_dir()
        if not TEMPLATES_DIR.exists():
            return "Error: templates directory not found."
        
        files = [f.name for f in TEMPLATES_DIR.glob("*") if f.is_file()]
        return "\n".join(sorted(files))

    @mcp.tool(
        name="read_template",
        annotations={
            "title": "Read Template",
            "readOnlyHint": True,
            "description": "Reads the content of a specific code template."
        }
    )
    def read_template(filename: str = Field(..., description="Filename of the template (e.g. 'CellType.cs.txt')")) -> str:
        """Reads the content of a specific code template."""
        ensure_base_dir()
        file_path = TEMPLATES_DIR / filename
        
        # Security check: ensure path is within TEMPLATES_DIR
        try:
            file_path.resolve().relative_to(TEMPLATES_DIR.resolve())
        except ValueError:
            return "Error: Invalid file path. Must be within templates directory."

        if not file_path.exists():
            return f"Error: Template '{filename}' not found."
            
        return file_path.read_text(encoding="utf-8")

    @mcp.tool(
        name="list_icons",
        annotations={
            "title": "List Icons",
            "readOnlyHint": True,
            "description": "Lists all available plugin icons."
        }
    )
    def list_icons() -> str:
        """Lists all available plugin icons."""
        ensure_base_dir()
        if not ICONS_DIR.exists():
            return "Error: icons directory not found."
        
        files = [f.name for f in ICONS_DIR.glob("*.svg") if f.is_file()]
        return "\n".join(sorted(files))

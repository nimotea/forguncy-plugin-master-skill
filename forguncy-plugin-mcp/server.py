from typing import List, Optional
from pathlib import Path
import os
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# Initialize the MCP server
mcp = FastMCP("forguncy_plugin_mcp")

# Configuration
# Assuming the skill directory is sibling to this mcp directory
BASE_DIR = Path(__file__).parent.parent / "forguncy-plugin-master-skill"
DOCS_DIR = BASE_DIR / "docs"
TEMPLATES_DIR = BASE_DIR / "templates"
SKILL_FILE = BASE_DIR / "SKILL.md"

def _ensure_base_dir():
    if not BASE_DIR.exists():
        raise FileNotFoundError(f"Base directory not found at {BASE_DIR}")

# Tool Input Models
class ReadDocInput(BaseModel):
    path: str = Field(..., description="Relative path to the document within docs/ folder (e.g. 'SOP.md' or 'references/CellType/Basic_Structure.md')")

class ReadTemplateInput(BaseModel):
    filename: str = Field(..., description="Filename of the template (e.g. 'CellType.cs.txt')")

# Tools

@mcp.tool(
    name="get_skill_overview",
    annotations={
        "title": "Get Skill Overview (SKILL.md)",
        "readOnlyHint": True,
        "description": "Reads the main SKILL.md file which contains the overview and core instructions for Forguncy Plugin development."
    }
)
def get_skill_overview() -> str:
    """Reads the main SKILL.md file."""
    _ensure_base_dir()
    if not SKILL_FILE.exists():
        return "Error: SKILL.md not found."
    return SKILL_FILE.read_text(encoding="utf-8")

@mcp.tool(
    name="list_docs",
    annotations={
        "title": "List Documentation Files",
        "readOnlyHint": True,
        "description": "Lists all available documentation files in the docs directory."
    }
)
def list_docs() -> str:
    """Lists all available documentation files."""
    _ensure_base_dir()
    if not DOCS_DIR.exists():
        return "Error: docs directory not found."
    
    files = []
    for root, _, filenames in os.walk(DOCS_DIR):
        for filename in filenames:
            if filename.endswith(".md"):
                rel_path = Path(root) / filename
                files.append(str(rel_path.relative_to(DOCS_DIR)))
    
    return "\n".join(sorted(files))

@mcp.tool(
    name="read_doc",
    annotations={
        "title": "Read Documentation File",
        "readOnlyHint": True,
        "description": "Reads the content of a specific documentation file."
    }
)
def read_doc(params: ReadDocInput) -> str:
    """Reads the content of a specific documentation file."""
    _ensure_base_dir()
    file_path = DOCS_DIR / params.path
    
    # Security check: ensure path is within DOCS_DIR
    try:
        file_path.resolve().relative_to(DOCS_DIR.resolve())
    except ValueError:
        return "Error: Invalid file path. Must be within docs directory."
        
    if not file_path.exists():
        return f"Error: File '{params.path}' not found."
        
    return file_path.read_text(encoding="utf-8")

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
    _ensure_base_dir()
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
def read_template(params: ReadTemplateInput) -> str:
    """Reads the content of a specific code template."""
    _ensure_base_dir()
    file_path = TEMPLATES_DIR / params.filename
    
    # Security check: ensure path is within TEMPLATES_DIR
    try:
        file_path.resolve().relative_to(TEMPLATES_DIR.resolve())
    except ValueError:
        return "Error: Invalid file path. Must be within templates directory."

    if not file_path.exists():
        return f"Error: Template '{params.filename}' not found."
        
    return file_path.read_text(encoding="utf-8")

if __name__ == "__main__":
    mcp.run()

from typing import List, Optional, Dict
from pathlib import Path
import os
import re
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

class SearchDocsInput(BaseModel):
    query: str = Field(..., description="Keywords to search in documentation (e.g. 'DataAccess', 'Formula', 'ListView')")

class GetContextInput(BaseModel):
    plugin_type: str = Field(..., description="Type of plugin to get context for. Options: 'ServerCommand', 'CellType', 'ClientCommand', 'ServerApi', 'Middleware'")

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

@mcp.tool(
    name="search_docs",
    annotations={
        "title": "Search Documentation",
        "readOnlyHint": True,
        "description": "Searches for keywords in all documentation files and returns matching snippets."
    }
)
def search_docs(params: SearchDocsInput) -> str:
    """Searches for keywords in documentation files."""
    _ensure_base_dir()
    results = []
    query_lower = params.query.lower()
    
    for root, _, filenames in os.walk(DOCS_DIR):
        for filename in filenames:
            if filename.endswith(".md"):
                file_path = Path(root) / filename
                try:
                    content = file_path.read_text(encoding="utf-8")
                    lines = content.splitlines()
                    for i, line in enumerate(lines):
                        if query_lower in line.lower():
                            rel_path = file_path.relative_to(DOCS_DIR)
                            # Get some context (previous line and next line)
                            context_start = max(0, i - 1)
                            context_end = min(len(lines), i + 2)
                            snippet = "\n".join(lines[context_start:context_end])
                            results.append(f"File: {rel_path}\nLine {i+1}:\n{snippet}\n---")
                            if len(results) >= 20: # Limit results
                                break
                except Exception:
                    continue # Skip files that can't be read
            if len(results) >= 20:
                break
                
    if not results:
        return f"No matches found for '{params.query}'."
        
    return "\n".join(results)

@mcp.tool(
    name="get_plugin_type_context",
    annotations={
        "title": "Get Plugin Type Context",
        "readOnlyHint": True,
        "description": "Returns a curated list of documentation and templates for a specific plugin type (ServerCommand, CellType, etc.)."
    }
)
def get_plugin_type_context(params: GetContextInput) -> str:
    """Returns context (doc list, template) for a plugin type."""
    
    ptype = params.plugin_type
    
    # Define mapping of types to relevant files
    context_map = {
        "ServerCommand": {
            "template": "ServerCommand.cs.txt",
            "docs_dir": "references/ServerCommand",
            "key_docs": [
                "references/ServerCommand/Basic_Structure.md",
                "references/ServerCommand/Process_Exception_Handling.md",
                "references/ServerCommand/Other_Database_Interaction.md"
            ]
        },
        "CellType": {
            "template": "CellType.cs.txt",
            "docs_dir": "references/CellType",
            "key_docs": [
                "references/CellType/Basic_Structure.md",
                "references/CellType/Integration_Lifecycle.md",
                "references/CellType/Designer_Preview.md"
            ]
        },
        "ClientCommand": {
            "template": "ClientCommand.cs.txt",
            "docs_dir": "references/ClientCommand",
            "key_docs": ["references/ClientCommand/README.md"]
        },
        "ServerApi": {
            "template": "ServerApi.cs.txt",
            "docs_dir": "references/ServerApi",
            "key_docs": ["references/ServerApi/README.md"]
        },
        "Middleware": {
            "template": "Middleware.cs.txt",
            "docs_dir": "references/Middleware",
            "key_docs": ["references/Middleware/README.md"]
        }
    }
    
    if ptype not in context_map:
        return f"Error: Unknown plugin type '{ptype}'. Available types: {', '.join(context_map.keys())}"
        
    info = context_map[ptype]
    
    output = [f"# Context for {ptype}"]
    output.append(f"\n## Recommended Template")
    output.append(f"- {info['template']}")
    
    output.append(f"\n## Key Documentation (Start Here)")
    for doc in info['key_docs']:
        output.append(f"- {doc}")
        
    output.append(f"\n## All Related Documentation")
    _ensure_base_dir()
    docs_path = DOCS_DIR / info['docs_dir']
    if docs_path.exists():
        for f in docs_path.glob("*.md"):
            rel = f.relative_to(DOCS_DIR)
            output.append(f"- {rel}")
            
    return "\n".join(output)

if __name__ == "__main__":
    mcp.run()

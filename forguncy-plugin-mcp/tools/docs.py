from mcp.server.fastmcp import FastMCP
from pydantic import Field
import os
from pathlib import Path
from config import DOCS_DIR, SKILL_FILE, ensure_base_dir

def register(mcp: FastMCP):
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
        ensure_base_dir()
        if not SKILL_FILE.exists():
            return "Error: SKILL.md not found."
        return SKILL_FILE.read_text(encoding="utf-8")

    @mcp.tool(
        name="get_sop",
        annotations={
            "title": "Get SOP (Standard Operating Procedure)",
            "readOnlyHint": True,
            "description": "Reads the SOP.md file which contains the standard operating procedures for development."
        }
    )
    def get_sop() -> str:
        """Reads the SOP.md file."""
        ensure_base_dir()
        sop_file = DOCS_DIR / "SOP.md"
        if not sop_file.exists():
            return "Error: SOP.md not found."
        return sop_file.read_text(encoding="utf-8")

    @mcp.tool(
        name="list_docs",
        annotations={
            "title": "List Documentation Files",
            "readOnlyHint": True,
            "description": "Lists all available documentation files in the references directory."
        }
    )
    def list_docs() -> str:
        """Lists all available documentation files."""
        ensure_base_dir()
        if not DOCS_DIR.exists():
            return "Error: references directory not found."
        
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
    def read_doc(path: str = Field(..., description="Relative path to the document within references/ folder (e.g. 'SOP.md' or 'CellType/Basic_Structure.md')")) -> str:
        """Reads the content of a specific documentation file."""
        ensure_base_dir()
        file_path = DOCS_DIR / path
        
        # Security check: ensure path is within DOCS_DIR
        try:
            file_path.resolve().relative_to(DOCS_DIR.resolve())
        except ValueError:
            return "Error: Invalid file path. Must be within references directory."
            
        if not file_path.exists():
            return f"Error: File '{path}' not found."
            
        return file_path.read_text(encoding="utf-8")

    @mcp.tool(
        name="search_docs",
        annotations={
            "title": "Search Documentation",
            "readOnlyHint": True,
            "description": "Searches for keywords in all documentation files and returns matching snippets."
        }
    )
    def search_docs(query: str = Field(..., description="Keywords to search in documentation (e.g. 'DataAccess', 'Formula', 'ListView')")) -> str:
        """Searches for keywords in documentation files."""
        ensure_base_dir()
        results = []
        query_lower = query.lower()
        
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
            return f"No matches found for '{query}'."
            
        return "\n".join(results)

    @mcp.tool(
        name="get_plugin_type_context",
        annotations={
            "title": "Get Plugin Type Context",
            "readOnlyHint": True,
            "description": "Returns a curated list of documentation and templates for a specific plugin type (ServerCommand, CellType, etc.)."
        }
    )
    def get_plugin_type_context(plugin_type: str = Field(..., description="Type of plugin to get context for. Options: 'ServerCommand', 'CellType', 'ClientCommand', 'ServerApi', 'Middleware'")) -> str:
        """Returns context (doc list, template) for a plugin type."""
        
        ptype = plugin_type
        
        # Define mapping of types to relevant files
        context_map = {
            "ServerCommand": {
                "template": "ServerCommand.cs.txt",
                "docs_dir": "ServerCommand",
                "key_docs": [
                    "ServerCommand/Basic_Structure.md",
                    "ServerCommand/Process_Exception_Handling.md",
                    "ServerCommand/Other_Database_Interaction.md"
                ]
            },
            "CellType": {
                "template": "CellType.cs.txt",
                "docs_dir": "CellType",
                "key_docs": [
                    "CellType/Basic_Structure.md",
                    "CellType/Integration_Lifecycle.md",
                    "CellType/Designer_Preview.md"
                ]
            },
            "ClientCommand": {
                "template": "ClientCommand.cs.txt",
                "docs_dir": "ClientCommand",
                "key_docs": ["ClientCommand/README.md"]
            },
            "ServerApi": {
                "template": "ServerApi.cs.txt",
                "docs_dir": "ServerApi",
                "key_docs": ["ServerApi/README.md"]
            },
            "Middleware": {
                "template": "Middleware.cs.txt",
                "docs_dir": "Middleware",
                "key_docs": ["Middleware/README.md"]
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
        ensure_base_dir()
        docs_path = DOCS_DIR / info['docs_dir']
        if docs_path.exists():
            for f in docs_path.glob("*.md"):
                rel = f.relative_to(DOCS_DIR)
                output.append(f"- {rel}")
                
        return "\n".join(output)

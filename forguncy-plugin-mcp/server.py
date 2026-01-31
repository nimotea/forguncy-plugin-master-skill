from typing import List, Optional, Dict
from pathlib import Path
import os
import re
import subprocess
from mcp.server.fastmcp import FastMCP
from pydantic import Field
from config import BASE_DIR, DOCS_DIR, TEMPLATES_DIR, SKILL_FILE, ICONS_DIR, SCRIPTS_DIR, ensure_base_dir, find_plugin_project

# Initialize the MCP server
mcp = FastMCP("forguncy_plugin_mcp")

# Tool Input Models
# Models removed in favor of direct parameters for better compatibility

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

@mcp.tool(
    name="get_powershell_command",
    annotations={
        "title": "Get PowerShell Compatible Command",
        "description": "Converts a standard shell command (using &&) to a PowerShell compatible command (using ; or script block)."
    }
)
def get_powershell_command(command: str = Field(..., description="The command to convert (e.g. 'cd dir && npm install')")) -> str:
    """Converts a command to PowerShell compatible format."""
    # Replace && with ;
    ps_command = command.replace(" && ", "; ")
    return f"In PowerShell, use ';' instead of '&&':\n\n{ps_command}"

@mcp.tool(
    name="validate_plugin_project",
    annotations={
        "title": "Validate Forguncy Plugin Project",
        "description": "Checks the current directory for Forguncy plugin project structure and common configuration issues."
    }
)
def validate_plugin_project(project_path: Optional[str] = Field(None, description="Path to the project directory. If not provided, searches upwards from current directory.")) -> str:
    """Validates the Forguncy plugin project structure."""
    cwd = Path(project_path) if project_path else Path.cwd()
    project_dir = find_plugin_project(cwd)
    
    if not project_dir:
        return "Error: No Forguncy plugin project (.csproj) found in the specified directory or its parents."
    
    results = [f"# Validation Results for {project_dir.name}"]
    issues = []
    
    # 1. Check for .csproj
    csproj_files = list(project_dir.glob("*.csproj"))
    if not csproj_files:
        issues.append("- Missing .csproj file.")
    else:
        csproj = csproj_files[0]
        content = csproj.read_text(encoding="utf-8")
        
        # Check for AssemblyName and RootNamespace
        if "<AssemblyName>" not in content:
            issues.append("- <AssemblyName> is missing in .csproj. This might cause issues with Forguncy registration.")
        if "<RootNamespace>" not in content:
            issues.append("- <RootNamespace> is missing in .csproj.")
            
        # Check for Forguncy references
        if "GrapeCity.Forguncy" not in content and "Forguncy." not in content:
            issues.append("- No Forguncy SDK references found in .csproj.")

    # 2. Check for PluginConfig.json (optional but recommended for some types)
    config_json = project_dir / "PluginConfig.json"
    if config_json.exists():
        results.append("- Found PluginConfig.json")
    
    # 3. Check for Resources or Icons
    icon_files = list(project_dir.glob("**/icon.png")) + list(project_dir.glob("**/*.svg"))
    if not icon_files:
        issues.append("- No icon file (icon.png or .svg) found. Plugins should have an icon.")

    if not issues:
        results.append("\n✅ Project structure looks valid!")
    else:
        results.append("\n❌ Found the following issues:")
        results.extend(issues)
        
    return "\n".join(results)

@mcp.tool(
    name="validate_plugin_config",
    annotations={
        "title": "Validate PluginConfig.json Consistency",
        "description": "Checks if the components (Commands, CellTypes, etc.) defined in PluginConfig.json actually exist in the source code."
    }
)
def validate_plugin_config(project_path: Optional[str] = Field(None, description="Path to the project directory.")) -> str:
    """Validates PluginConfig.json against source code."""
    cwd = Path(project_path) if project_path else Path.cwd()
    project_dir = find_plugin_project(cwd)
    
    if not project_dir:
        return "Error: No Forguncy plugin project found."
        
    config_file = project_dir / "PluginConfig.json"
    if not config_file.exists():
        return "Info: PluginConfig.json not found. This is normal if the plugin doesn't use it."
        
    try:
        import json
        config = json.loads(config_file.read_text(encoding="utf-8"))
        
        results = ["# PluginConfig.json Consistency Check"]
        issues = []
        
        # 1. Check for AssemblyName
        assembly_name = config.get("AssemblyName")
        if not assembly_name:
            issues.append("- 'AssemblyName' is missing in PluginConfig.json.")
            
        # 2. Check for Commands
        commands = config.get("Commands", [])
        for cmd in commands:
            name = cmd.get("ClassName")
            if name:
                # Search for the class name in .cs files
                found = False
                for cs_file in project_dir.glob("**/*.cs"):
                    if name in cs_file.read_text(encoding="utf-8"):
                        found = True
                        break
                if not found:
                    issues.append(f"- Command ClassName '{name}' defined in config but not found in any .cs files.")

        # 3. Check for CellTypes
        cell_types = config.get("CellTypes", [])
        for ct in cell_types:
            name = ct.get("ClassName")
            if name:
                found = False
                for cs_file in project_dir.glob("**/*.cs"):
                    if name in cs_file.read_text(encoding="utf-8"):
                        found = True
                        break
                if not found:
                    issues.append(f"- CellType ClassName '{name}' defined in config but not found in any .cs files.")

        if not issues:
            results.append("\n✅ All components in PluginConfig.json are present in source code.")
        else:
            results.append("\n❌ Found inconsistency issues:")
            results.extend(issues)
            results.append("\nTip: If you recently deleted a component, make sure to remove its entry from PluginConfig.json.")
            
        return "\n".join(results)
    except Exception as e:
        return f"Error parsing PluginConfig.json: {str(e)}"

@mcp.tool(
    name="run_skill_script",
    annotations={
        "title": "Run Skill Script",
        "description": "Executes one of the pre-defined maintenance scripts (e.g. update_references.ps1, package_skill.ps1)."
    }
)
def run_skill_script(script_name: str = Field(..., description="Name of the script to run (e.g. 'update_references.ps1')"), args: List[str] = []) -> str:
    """Runs a script from the scripts directory."""
    ensure_base_dir()
    script_path = SCRIPTS_DIR / script_name
    
    if not script_path.exists():
        available = [f.name for f in SCRIPTS_DIR.glob("*")]
        return f"Error: Script '{script_name}' not found. Available scripts: {', '.join(available)}"
    
    try:
        if script_name.endswith(".ps1"):
            cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script_path)] + args
        elif script_name.endswith(".py"):
            cmd = ["python", str(script_path)] + args
        else:
            return f"Error: Unsupported script type '{script_name}'."
            
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=False)
        
        output = [f"# Script Execution: {script_name}"]
        output.append(f"\n## STDOUT\n{result.stdout}")
        if result.stderr:
            output.append(f"\n## STDERR\n{result.stderr}")
        output.append(f"\nExit Code: {result.returncode}")
        
        return "\n".join(output)
    except Exception as e:
        return f"Error executing script: {str(e)}"

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Forguncy Plugin MCP Server")
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse"], help="Transport protocol to use (stdio or sse)")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on for SSE transport")
    parser.add_argument("--host", default="0.0.0.0", help="Host to listen on for SSE transport")
    
    args = parser.parse_args()
    
    if args.transport == "sse":
        print(f"Starting SSE server on {args.host}:{args.port}...")
        mcp.settings.host = args.host
        mcp.settings.port = args.port
        mcp.run(transport="sse")
    else:
        mcp.run()

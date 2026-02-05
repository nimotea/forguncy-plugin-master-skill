from mcp.server.fastmcp import FastMCP
from pydantic import Field
from typing import Optional
from pathlib import Path
import json
from config import find_plugin_project

def register(mcp: FastMCP):
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

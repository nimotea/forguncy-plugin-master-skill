from mcp.server.fastmcp import FastMCP
from pydantic import Field
from typing import List
import subprocess
from config import SCRIPTS_DIR, ensure_base_dir

def register(mcp: FastMCP):
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

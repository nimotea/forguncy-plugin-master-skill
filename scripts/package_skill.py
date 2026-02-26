#!/usr/bin/env python3
"""
Skill Packager - Creates a distributable .skill file of a skill folder

Usage:
    python scripts/package_skill.py [skill_name_or_path] --output [output-directory]
"""

import sys
import zipfile
import os
import shutil
import json
import argparse
from pathlib import Path

# Add scripts directory to path to import quick_validate
sys.path.append(str(Path(__file__).parent))
try:
    from quick_validate import validate_skill
except ImportError:
    # Fallback or simple validation if quick_validate is missing in scripts dir
    def validate_skill(path):
        return True, "Skipping validation (module not found)"


def get_version(skill_path):
    """
    Read version from package.json in skill root, default to 1.0.0.
    """
    package_json_file = Path(skill_path) / "package.json"
    if package_json_file.exists():
        try:
            with open(package_json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("version", "1.0.0")
        except Exception as e:
            print(f"⚠️ Warning: Could not read package.json: {e}")
    return "1.0.0"


def create_package_json(output_path, skill_name, version):
    """
    Create a minimal package.json for npm link support.
    """
    package_json = {
        "name": f"{skill_name}-distribution",
        "version": version,
        "description": "Forguncy Plugin Master Skill Distribution",
        "private": True,
        "files": [
            "**/*"
        ]
    }
    
    with open(output_path / "package.json", "w", encoding="utf-8") as f:
        json.dump(package_json, f, indent=2)
    print(f"📄 Created package.json in {output_path} with version {version}")


def create_readme(output_path, skill_name):
    """
    Create a minimal README.md for the skill package.
    """
    content = f"""# {skill_name}

This is a distribution package for the {skill_name} skill.

## Installation

### 1. General Installation
To install this skill locally for most agents:

```bash
npx skills add . --skill {skill_name}
```

### 2. Specific Agent Installation (Recommended)
To ensure the skill is correctly recognized by your specific AI tool, add the `--agent` flag:

**For Claude Code:**
```bash
npx skills add . --skill {skill_name} --agent claude-code
```

**For Cursor:**
```bash
npx skills add . --skill {skill_name} --agent cursor
```

**For VS Code / Copilot:**
```bash
npx skills add . --skill {skill_name} --agent vscode
```

> **Note**: If your agent is not listed above, check the [official documentation](https://github.com/microsoft/skills) or try installing without the `--agent` flag to use the default shared location.

### Troubleshooting
If the skill is installed but not visible in your tool (e.g., Claude Code), it might be installed in a generic location. Try reinstalling with the explicit `--agent` flag as shown above.
"""
    with open(output_path / "README.md", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"📄 Created README.md in {output_path}")


def package_skill(skill_input, output_dir=None, format='folder'):
    """
    Package a skill folder into a build directory or .skill file.
    """
    # Determine skill path
    # 1. Check if input is a valid path
    input_path = Path(skill_input).resolve()
    if input_path.exists() and input_path.is_dir():
        skill_path = input_path
    else:
        # 2. Check if input is a skill name in src/skills
        repo_root = Path(__file__).parent.parent
        candidate_path = repo_root / "src" / "skills" / skill_input
        if candidate_path.exists() and candidate_path.is_dir():
            skill_path = candidate_path
        else:
             print(f"❌ Error: Skill not found at {input_path} or {candidate_path}")
             return None

    print(f"📦 Packaging skill from: {skill_path}")

    # Get version
    version = get_version(skill_path)
    print(f"📌 Version: {version}")

    # Run validation
    print("🔍 Validating skill...")
    valid, message = validate_skill(skill_path)
    if not valid:
        print(f"❌ Validation failed: {message}")
        return None
    print(f"✅ {message}\n")

    # Determine output location
    skill_name = skill_path.name
    if output_dir:
        output_path = Path(output_dir).resolve()
    else:
        output_path = Path.cwd() / "build"
    
    # Clean and recreate output directory if building folder
    # Always build folder first, then zip if needed
    if output_path.exists():
        shutil.rmtree(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    # Files to exclude from the package (dev tools)
    EXCLUDED_FILES = {'package_skill.py', 'package_skill.ps1', 'quick_validate.py', '.DS_Store', 'VERSION', 'package.json'}
    EXCLUDED_DIRS = {'.git', '.trae', '__pycache__', 'build', 'dist', 'node_modules', 'scripts'}

    try:
        print(f"📂 Building skill to directory: {output_path}")
        
        # Create standard skills structure: output/skills/skill_name/
        target_skill_dir = output_path / "skills" / skill_name
        target_skill_dir.mkdir(parents=True, exist_ok=True)

        # Copy files
        for root, dirs, files in os.walk(skill_path):
            # Modify dirs in-place to exclude unwanted directories
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            
            rel_path = Path(root).relative_to(skill_path)
            target_dir = target_skill_dir / rel_path
            target_dir.mkdir(parents=True, exist_ok=True)
            
            for file in files:
                if file.startswith('.') or file.endswith('.pyc') or file.endswith('.skill'):
                    continue
                if file in EXCLUDED_FILES:
                    continue
                    
                src_file = Path(root) / file
                dst_file = target_dir / file
                shutil.copy2(src_file, dst_file)
                print(f"  Copied: {rel_path / file}")
        
        # Create package.json and README.md in root output dir
        create_package_json(output_path, skill_name, version)
        create_readme(output_path, skill_name)
        
        # Handle Rules Distribution (Multi-IDE Support)
        # Source: assets/internal/forguncy-plugin-skill-apply.md
        internal_rule_src = skill_path / "assets" / "internal" / "forguncy-plugin-skill-apply.md"
        
        if internal_rule_src.exists():
            print(f"⚙️  Processing IDE rules from: {internal_rule_src}")
            
            # 1. Trae Support: .trae/rules/skill-apply.md
            trae_rules_dir = output_path / ".trae" / "rules"
            trae_rules_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(internal_rule_src, trae_rules_dir / "skill-apply.md")
            print(f"  Generated: .trae/rules/skill-apply.md")

            # 2. Cursor Support: .cursor/rules/skill-apply.mdc
            cursor_rules_dir = output_path / ".cursor" / "rules"
            cursor_rules_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(internal_rule_src, cursor_rules_dir / "skill-apply.mdc")
            print(f"  Generated: .cursor/rules/skill-apply.mdc")
            
        print(f"\n✅ Successfully built skill folder to: {output_path}")

        if format == 'zip':
            print(f"\n📦 Compressing to .skill file...")
            # Create zip from output_path
            # shutil.make_archive creates a zip file with base_name.zip
            archive_name = shutil.make_archive(str(output_path), 'zip', output_path)
            
            # Rename .zip to .skill
            skill_file_path = output_path.with_suffix('.skill')
            if skill_file_path.exists():
                os.remove(skill_file_path)
            
            os.rename(archive_name, skill_file_path)
            print(f"✅ Created skill package: {skill_file_path}")
            
            return skill_file_path

        return output_path

    except Exception as e:
        print(f"❌ Error processing skill: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Skill Packager")
    parser.add_argument("skill_input", nargs="?", help="Path to skill folder OR skill name (in src/skills)", default="forguncy-plugin-expert")
    parser.add_argument("--output", "-o", help="Output directory")
    parser.add_argument("--format", "-f", choices=['zip', 'folder'], default='folder', help="Output format (zip or folder)")
    
    args = parser.parse_args()

    package_skill(args.skill_input, args.output, args.format)


if __name__ == "__main__":
    main()

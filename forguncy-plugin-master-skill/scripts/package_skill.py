#!/usr/bin/env python3
"""
Skill Packager - Creates a distributable .skill file of a skill folder

Usage:
    python scripts/package_skill.py <path/to/skill-folder> [output-directory]
"""

import sys
import zipfile
import os
import shutil
import json
import argparse
from pathlib import Path
from quick_validate import validate_skill


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
        "name": skill_name.lower().replace(" ", "-"),
        "version": version,
        "description": "Forguncy Plugin Master Skill Documentation",
        "private": True,
        "files": [
            "**/*"
        ]
    }
    
    with open(output_path / "package.json", "w", encoding="utf-8") as f:
        json.dump(package_json, f, indent=2)
    print(f"📄 Created package.json in {output_path} with version {version}")


def package_skill(skill_path, output_dir=None, format='zip'):
    """
    Package a skill folder into a build directory or .skill file.
    """
    skill_path = Path(skill_path).resolve()

    # Validate skill folder exists
    if not skill_path.exists():
        print(f"❌ Error: Skill folder not found: {skill_path}")
        return None

    if not skill_path.is_dir():
        print(f"❌ Error: Path is not a directory: {skill_path}")
        return None

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
    if output_path.exists() and format == 'folder':
        shutil.rmtree(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    # Files to exclude from the package (dev tools)
    EXCLUDED_FILES = {'package_skill.py', 'package_skill.ps1', 'quick_validate.py', '.DS_Store', 'VERSION', 'package.json'}
    EXCLUDED_DIRS = {'.git', '.trae', '__pycache__', 'build', 'dist', 'node_modules'}

    try:
        if format == 'folder':
            print(f"📂 Building skill to directory: {output_path}")
            
            # Copy files
            for root, dirs, files in os.walk(skill_path):
                # Modify dirs in-place to exclude unwanted directories
                dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
                
                rel_path = Path(root).relative_to(skill_path)
                target_dir = output_path / rel_path
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
            
            # Create package.json
            create_package_json(output_path, skill_name, version)
            
            print(f"\n✅ Successfully built skill to: {output_path}")
            return output_path

        elif format == 'zip':
            skill_filename = output_path / f"{skill_name}.skill"
            print(f"📦 Creating package at: {skill_filename}")
            
            with zipfile.ZipFile(skill_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(skill_path):
                    dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
                    
                    for file in files:
                        if file.startswith('.') or file.endswith('.pyc') or file.endswith('.skill'):
                            continue
                        if file in EXCLUDED_FILES:
                            continue
                            
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(skill_path)
                        zipf.write(file_path, arcname)
                        print(f"  Added: {arcname}")

            print(f"\n✅ Successfully packaged skill to: {skill_filename}")
            return skill_filename

    except Exception as e:
        print(f"❌ Error processing skill: {e}")
        return None



def main():
    parser = argparse.ArgumentParser(description="Skill Packager")
    parser.add_argument("skill_path", nargs="?", help="Path to the skill folder")
    parser.add_argument("--output", "-o", help="Output directory")
    parser.add_argument("--format", "-f", choices=['zip', 'folder'], default='folder', help="Output format (zip or folder)")
    
    args = parser.parse_args()

    skill_path = args.skill_path
    if not skill_path:
        # Auto-detect logic
        cwd = Path.cwd()
        if cwd.name == 'scripts':
            skill_path = cwd.parent
        elif (cwd / 'SKILL.md').exists():
            skill_path = cwd
        else:
            print("❌ Error: Could not detect skill path. Please provide it as an argument.")
            sys.exit(1)

    package_skill(skill_path, args.output, args.format)


if __name__ == "__main__":
    main()


import os
import re

def clean_empty_files(base_dir):
    print("Cleaning empty or near-empty files...")
    count = 0
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.lower().endswith('.md'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    # Check if empty or just headers/html
                    if len(content) < 100 or content == "" or re.match(r'^#+\s+.*(\n+##\s+Content)?(\n+<p>.*</p>)?$', content, re.DOTALL):
                        print(f"  Deleting empty file: {file}")
                        os.remove(path)
                        count += 1
                except Exception as e:
                    print(f"  Error checking {file}: {e}")
    print(f"Deleted {count} empty files.\n")

def optimize_content(content):
    # 1. Remove Source line
    content = re.sub(r'^> Source: .*\n+', '', content)
    
    # 2. Remove Images
    content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
    content = re.sub(r'\*\[Image Omitted\]\*', '', content)

    # 3. Remove HTML tags like <br>
    content = re.sub(r'<br\s*/?>', '', content)
    content = re.sub(r'<p>.*?</p>', '', content, flags=re.DOTALL)

    # 4. Simplify Code Blocks (Aggressive optimization for AI)
    # Remove class wrappers but keep property definitions
    # Pattern: public class ... : ... { ... }
    # This is tricky with regex. Let's try a simpler approach:
    # If a code block contains "public class", we try to extract the property definition inside.
    
    # Actually, let's just keep the code blocks as is for now but remove the surrounding text if it's just filler.
    # The user said "not friendly to humans", so we can be concise.
    
    # Remove empty code blocks
    content = re.sub(r'```\w*\s*\n\s*```', '', content)
    
    # Remove multiple newlines
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content.strip()

def classify_properties(files):
    basic_patterns = [
        r'Boolean', r'Color', r'Decimal', r'Double', r'Enum', 
        r'Font', r'Formula', r'Integer', r'Percentage', r'String'
    ]
    
    basic_files = []
    complex_files = []
    
    for f in files:
        is_basic = False
        for p in basic_patterns:
            if re.search(p, f, re.IGNORECASE):
                is_basic = True
                break
        
        if is_basic:
            basic_files.append(f)
        else:
            complex_files.append(f)
            
    return basic_files, complex_files

def consolidate_optimized(base_dir, file_list, output_filename, title):
    if not file_list:
        return

    print(f"Consolidating {len(file_list)} files into {output_filename}...")
    
    with open(os.path.join(base_dir, output_filename), 'w', encoding='utf-8') as outfile:
        outfile.write(f"# {title}\n\n")
        
        for f_name in file_list:
            file_path = os.path.join(base_dir, f_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as infile:
                    content = infile.read()
                
                optimized = optimize_content(content)
                if optimized:
                    outfile.write(f"## {f_name.replace('.md', '').replace('_', ' ')}\n\n")
                    outfile.write(optimized)
                    outfile.write(f"\n\n---\n\n")
                
            except Exception as e:
                print(f"Error reading {f_name}: {e}")

def process_directory(base_dir):
    print(f"Processing {base_dir}...")
    
    # Gather all property files
    all_files = [f for f in os.listdir(base_dir) if f.endswith('.md')]
    property_files = [f for f in all_files if 'Addproperty' in f or 'Attribute_' in f] # Adjust based on naming
    
    # If we are in CellType/Reference_Manual, files are named Addproperty_*.md
    # If we are in ServerCommand/Reference_Manual, files are named Addproperty_*.md or Attribute_*.md
    
    if not property_files:
        print("  No property files found.")
        return

    basic_files, complex_files = classify_properties(property_files)
    
    consolidate_optimized(base_dir, basic_files, 'Properties_Basic.md', 'Basic Properties Reference')
    consolidate_optimized(base_dir, complex_files, 'Properties_Complex.md', 'Complex Properties Reference')
    
    # Remove old Properties.md if exists
    if os.path.exists(os.path.join(base_dir, 'Properties.md')):
        os.remove(os.path.join(base_dir, 'Properties.md'))
        print("  Removed old Properties.md")
        
    # Remove individual files after consolidation? 
    # The user asked to "consolidate", so we should probably remove the source files to reduce clutter.
    # But let's keep them for now or delete them? The previous script deleted them.
    # If the previous script ran, we only have Properties.md now!
    # Wait, the previous script deleted the source files?
    # Yes: "Deleting 22 files..."
    
    # So now we only have Properties.md!
    # We need to split Properties.md back into Basic and Complex?
    # Or we parse Properties.md and split it.
    
    pass

def split_existing_properties_file(file_path):
    if not os.path.exists(file_path):
        return

    print(f"Splitting existing {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Split by separator
    # The previous script used: "\n\n---\n\n<!-- Origin: ... -->\n\n"
    sections = re.split(r'\n---\n', content)
    
    basic_content = []
    complex_content = []
    
    basic_patterns = [
        r'Boolean', r'Color', r'Decimal', r'Double', r'Enum', 
        r'Font', r'Formula', r'Integer', r'Percentage', r'String'
    ]
    
    header = sections[0] # The main header of the file
    
    for section in sections[1:]:
        # Extract Origin
        match = re.search(r'<!-- Origin: (.*?) -->', section)
        if match:
            origin_name = match.group(1)
            
            is_basic = False
            for p in basic_patterns:
                if re.search(p, origin_name, re.IGNORECASE):
                    is_basic = True
                    break
            
            # Optimize the section content
            optimized_section = optimize_content(section)
            
            if is_basic:
                basic_content.append(optimized_section)
            else:
                complex_content.append(optimized_section)
    
    dir_path = os.path.dirname(file_path)
    
    with open(os.path.join(dir_path, 'Properties_Basic.md'), 'w', encoding='utf-8') as f:
        f.write("# Basic Properties Reference\n\n")
        f.write('\n\n---\n\n'.join(basic_content))
        
    with open(os.path.join(dir_path, 'Properties_Complex.md'), 'w', encoding='utf-8') as f:
        f.write("# Complex Properties Reference\n\n")
        f.write('\n\n---\n\n'.join(complex_content))
        
    print(f"  Created Properties_Basic.md and Properties_Complex.md")
    
    # Remove original
    os.remove(file_path)
    print(f"  Removed {file_path}")

def main():
    base_ref = r'e:\code\forguncy-plugin-master-skill\src\skills\forguncy-plugin-expert\references'
    
    # 1. Clean empty files first
    clean_empty_files(base_ref)
    
    # 2. Split Properties.md in CellType
    cell_props = os.path.join(base_ref, 'CellType', 'Reference_Manual', 'Properties.md')
    split_existing_properties_file(cell_props)
    
    # 3. Split Properties.md in ServerCommand
    srv_props = os.path.join(base_ref, 'ServerCommand', 'Reference_Manual', 'Properties.md')
    split_existing_properties_file(srv_props)
    
    # 4. Split Properties.md in ClientCommand
    cli_props = os.path.join(base_ref, 'ClientCommand', 'Properties.md')
    split_existing_properties_file(cli_props)

    # 5. Split Properties.md in JavaAdapter
    java_props = os.path.join(base_ref, 'JavaAdapter', 'Properties.md')
    split_existing_properties_file(java_props)

if __name__ == '__main__':
    main()

import os
import yaml
from pathlib import Path

def process_includes(content, base_path):
    lines = []
    for line in content.split('\n'):
        if line.strip().startswith('--8<--'):
            include_path = line.split('"')[1]
            full_path = base_path.parent / include_path
            if full_path.exists():
                lines.append(process_file(full_path))
        else:
            lines.append(line)
    return '\n'.join(lines)

def process_file(path):
    with open(path) as f:
        content = f.read()
    return process_includes(content, path)

def main():
    docs_dir = Path('docs')
    output = []
    
    with open('nav.yml') as f:
        nav = yaml.safe_load(f)
    
    for section in nav:
        if isinstance(section, dict):
            for title, items in section.items():
                output.append(f'# {title}')
                process_items(items, output, docs_dir)
        else:
            path = docs_dir / section
            output.append(process_file(path))
    with open('n8n-docs.md', 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(output))

def process_items(items, output, docs_dir):
    """
    Process documentation items recursively and append their content to the output list.

    Args:
        items: List of items to process, can be dictionaries (for nested sections) or strings (file paths)
        output: List to append processed content to
        docs_dir: Path object representing the base documentation directory

    The function handles both nested sections (dictionaries) and individual files/directories,
    recursively processing all markdown files found and adding their content to the output list.
    """
    for item in items:
        if isinstance(item, dict):
            for sub_title, sub_items in item.items():
                output.append(f'## {sub_title}')
                process_items(sub_items, output, docs_dir)
        else:
            path = docs_dir / item
            if not path.exists():
                print(f"⚠️ Navigation entry '{item}' not found at {path}")
                continue
            try:
                if path.is_dir():
                    print(f"Processing directory: {path}")
                    for md_file in path.glob('**/*.md'):
                        output.append(process_file(md_file))
                else:
                    print(f"Processing file: {path}")
                    output.append(process_file(path))
            except Exception as e:
                print(f"🚨 Error processing {path}: {str(e)}")

if __name__ == '__main__':
    main()
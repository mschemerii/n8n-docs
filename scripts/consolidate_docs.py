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
    in_frontmatter = False
    content_lines = []
    current_url = None
    for line in content.split('\n'):
        if line.startswith('---'):
            in_frontmatter = not in_frontmatter
            continue
        if line.startswith('#https://'):
            current_url = line[1:].strip()
            continue
        if line.startswith('description: ') and current_url:
            title = line.split('description: ')[1].strip()
            content_lines.append(f'## [{title}]({current_url})\n')
            current_url = None
            continue
        content_lines.append(line)
    processed_content = '\n'.join(content_lines)
    return process_includes(processed_content, path)

def process_navigation():
    # Load MkDocs configuration for validation
    mkdocs_config = yaml.safe_load(open('../mkdocs.yml'))
    
    # Process nav.yml with MkDocs validation rules
    nav = yaml.safe_load(open('../nav.yml'))
    validated_nav = validate_nav_structure(nav, mkdocs_config)
    
    # New frontmatter parsing logic
    for section in validated_nav:
        process_section(section)

def validate_nav_structure(nav, config):
    """Validate navigation against MkDocs configuration rules"""
    validated = []
    omitted_files = config.get('validation', {}).get('nav', {}).get('omitted_files', [])
    allow_absolute = config.get('validation', {}).get('nav', {}).get('absolute_links', 'ignore')

    for item in nav:
        if isinstance(item, dict):
            for title, children in item.items():
                filtered = [c for c in children 
                          if not (isinstance(c, str) and any(c.endswith(f) for f in omitted_files))]
                if filtered:
                    validated.append({title: validate_nav_structure(filtered, config)})
        elif isinstance(item, str):
            if not any(item.endswith(f) for f in omitted_files):
                if item.startswith('http') and allow_absolute == 'warn':
                    print(f"⚠️ Absolute link found: {item}")
                validated.append(item)
    return validated

def process_section(section, depth=1):
    """Process navigation section with proper header hierarchy"""
    if isinstance(section, dict):
        for title, items in section.items():
            yield f"{'#' * depth} {title}\n"
            for item in items:
                yield from process_section(item, depth+1)
    elif isinstance(section, list):
        for item in section:
            yield from process_section(item, depth)
    else:
        path = Path('docs') / section
        if path.exists():
            yield process_file(path)

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
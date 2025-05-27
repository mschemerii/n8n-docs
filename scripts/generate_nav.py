import yaml
from pathlib import Path

def generate_nav():
    docs_dir = Path('docs')
    nav_structure = []

    # Process main categories
    for entry in docs_dir.iterdir():
        if entry.is_dir() and not entry.name.startswith('_'):
            category = {entry.name: []}
            # Process subdirectories
            for sub_entry in entry.glob('**/*.md'):
                rel_path = sub_entry.relative_to(docs_dir)
                category[entry.name].append(str(rel_path))
            nav_structure.append(category)

    # Write to nav.yml
    with open('nav.yml', 'w') as f:
        yaml.safe_dump(nav_structure, f, default_flow_style=False)

if __name__ == '__main__':
    generate_nav()
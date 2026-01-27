#!/usr/bin/env python3
"""Debug script for parse_task_metadata function."""

import re
from pathlib import Path

def parse_task_metadata_debug(content: str) -> dict:
    """Debug version of parse_task_metadata function."""
    print(f"Input content length: {len(content)}")
    print(f"First 100 chars: {repr(content[:100])}")
    
    metadata = {
        "title": "Untitled Task",
        "priority": "medium",
        "source": "unknown",
        "risk_score": 0.3,
        "complexity_score": 0.3,
        "description": content[:300] if len(content) > 300 else content
    }

    # Extract YAML frontmatter
    print("Attempting to match YAML frontmatter...")
    yaml_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    print(f"yaml_match result: {yaml_match}")
    
    if yaml_match:
        print("YAML frontmatter found!")
        yaml_content = yaml_match.group(1)
        print(f"YAML content: {repr(yaml_content)}")

        # Parse key-value pairs
        for line in yaml_content.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                print(f"Parsing: {key} = {value}")

                if key == 'type':
                    metadata['source'] = value
                elif key == 'priority':
                    metadata['priority'] = value
                elif key == 'subject' or key == 'title':
                    metadata['title'] = value
                elif key == 'risk_score':
                    try:
                        metadata['risk_score'] = float(value)
                    except:
                        pass
                elif key == 'complexity_score':
                    try:
                        metadata['complexity_score'] = float(value)
                    except:
                        pass
    else:
        print("No YAML frontmatter found")

    # Try to extract title from content if not in frontmatter
    if metadata['title'] == "Untitled Task":
        # Look for ## heading
        heading_match = re.search(r'^##\s+(.+)$', content, re.MULTILINE)
        print(f"Heading match: {heading_match}")
        if heading_match:
            metadata['title'] = heading_match.group(1).strip()
        else:
            # Use first line after frontmatter
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('---') and not line.startswith('#'):
                    metadata['title'] = line[:80]
                    break

    # Detect priority from content
    content_lower = content.lower()
    if 'urgent' in content_lower or 'asap' in content_lower:
        metadata['priority'] = 'urgent'
    elif 'high priority' in content_lower or 'important' in content_lower:
        metadata['priority'] = 'high'
    elif 'low priority' in content_lower:
        metadata['priority'] = 'low'

    # Get description after frontmatter
    print(f"yaml_match at end: {yaml_match}")
    if yaml_match:
        desc_start = yaml_match.end()
        desc_content = content[desc_start:].strip()
        metadata['description'] = desc_content[:500] if len(desc_content) > 500 else desc_content
    else:
        # If no YAML frontmatter, use the whole content as description
        metadata['description'] = content[:500] if len(content) > 500 else content

    print(f"Final metadata: {metadata}")
    return metadata

# Test with a sample file
if __name__ == "__main__":
    vault_path = Path("../../Vault/Needs_Action")
    sample_file = list(vault_path.glob("*.md"))[0] if list(vault_path.glob("*.md")) else None
    
    if sample_file:
        print(f"Testing with file: {sample_file}")
        content = sample_file.read_text(encoding='utf-8', errors='replace')
        result = parse_task_metadata_debug(content)
        print("\nResult:", result)
    else:
        print("No sample file found in Needs_Action")
        
    # Test with a simple example
    print("\nTesting with simple example:")
    simple_content = """---
type: email_reply
priority: high
---
## Reply to Important Client

Need to respond to the client's urgent request about the project timeline."""
    result = parse_task_metadata_debug(simple_content)
    print("\nSimple result:", result)
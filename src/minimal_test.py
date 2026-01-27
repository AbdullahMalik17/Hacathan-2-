#!/usr/bin/env python3
"""
Minimal test for the API server to isolate the issue.
"""

import sys
from pathlib import Path
import re

# Add src to path for imports
SRC_DIR = Path(__file__).parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

def parse_task_metadata(content: str):
    """Parse YAML frontmatter and extract task metadata."""
    import re

    metadata = {
        "title": "Untitled Task",
        "priority": "medium",
        "source": "unknown",
        "risk_score": 0.3,
        "complexity_score": 0.3,
        "description": content[:300] if len(content) > 300 else content
    }

    # Extract YAML frontmatter
    yaml_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if yaml_match:
        yaml_content = yaml_match.group(1)

        # Parse key-value pairs
        for line in yaml_content.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()

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

    # Try to extract title from content if not in frontmatter
    if metadata['title'] == "Untitled Task":
        # Look for ## heading
        heading_match = re.search(r'^##\s+(.+)$', content, re.MULTILINE)
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
    if yaml_match:
        desc_start = yaml_match.end()
        desc_content = content[desc_start:].strip()
        metadata['description'] = desc_content[:500] if len(desc_content) > 500 else desc_content
    else:
        # If no YAML frontmatter, use the whole content as description
        metadata['description'] = content[:500] if len(content) > 500 else content

    return metadata

# Test with a problematic file
if __name__ == "__main__":
    PROJECT_ROOT = Path(__file__).parent.parent
    VAULT_PATH = PROJECT_ROOT / "Vault"
    
    # Get a file from Needs_Action
    needs_action = VAULT_PATH / "Needs_Action"
    if needs_action.exists():
        files = list(needs_action.glob("*.md"))
        if files:
            test_file = files[0]
            print(f"Testing with file: {test_file}")
            
            try:
                content = test_file.read_text(encoding='utf-8', errors='replace')
                print(f"Content length: {len(content)}")
                
                # Test the parse function
                result = parse_task_metadata(content)
                print(f"Success! Parsed title: {result['title'][:50]}...")
                print(f"Full result keys: {list(result.keys())}")
            except Exception as e:
                print(f"Error parsing file: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("No files in Needs_Action")
    else:
        print("Needs_Action directory doesn't exist")
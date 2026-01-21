import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("ContactManager")

PROJECT_ROOT = Path(__file__).parent.parent.parent
CONTACTS_FILE = PROJECT_ROOT / "config" / "known_contacts.json"

def load_contacts() -> Dict[str, Any]:
    """Load known contacts from config."""
    if not CONTACTS_FILE.exists():
        # Create empty if doesn't exist
        with open(CONTACTS_FILE, "w") as f:
            json.dump({}, f, indent=2)
        return {}
    
    try:
        with open(CONTACTS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load contacts: {e}")
        return {}

def is_known_contact(name: str) -> bool:
    """Check if a contact name is in the known list."""
    contacts = load_contacts()
    return name in contacts

def get_contact_info(name: str) -> Optional[Dict[str, Any]]:
    """Get info for a known contact."""
    contacts = load_contacts()
    return contacts.get(name)

def add_contact(name: str, info: Dict[str, Any]):
    """Add or update a contact."""
    contacts = load_contacts()
    contacts[name] = info
    with open(CONTACTS_FILE, "w") as f:
        json.dump(contacts, f, indent=2)

"""
Digital FTE Watchers Package

Watchers are daemon processes that monitor external sources
and create task files in the Obsidian vault.
"""

from .gmail_watcher import main as gmail_watcher_main
from .whatsapp_watcher import main as whatsapp_watcher_main
from .filesystem_watcher import main as filesystem_watcher_main

__all__ = [
    'gmail_watcher_main',
    'whatsapp_watcher_main',
    'filesystem_watcher_main'
]

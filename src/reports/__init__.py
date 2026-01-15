"""
Digital FTE Reports Package

Reports provide visibility into the Digital FTE's activities
and system health.
"""

from .ceo_briefing import main as generate_ceo_briefing

__all__ = ['generate_ceo_briefing']

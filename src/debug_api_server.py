#!/usr/bin/env python3
"""
Test version of api_server to debug the issue.
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add src to path for imports
SRC_DIR = Path(__file__).parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Import notification API - try multiple import paths
try:
    from notifications.api import router as notifications_router
    print("Successfully imported notifications.router")
except ImportError as e:
    print(f"Failed to import notifications.api: {e}")
    try:
        from src.notifications.api import router as notifications_router
        print("Successfully imported src.notifications.api")
    except ImportError as e2:
        print(f"Failed to import both paths: {e2}")
        notifications_router = None
        print("[API Server] Warning: Notifications module not found")

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
VAULT_PATH = PROJECT_ROOT / "Vault"

print(f"VAULT_PATH: {VAULT_PATH}")
print(f"VAULT_PATH exists: {VAULT_PATH.exists()}")

# Initialize FastAPI
app = FastAPI(
    title="Abdullah Junior API",
    description="Backend API for Digital FTE with Agentic Intelligence",
    version="2.0.0"
)

# CORS for frontend and mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8081",  # Expo dev server
        "http://10.0.2.2:8000",   # Android emulator
        "https://abdullahjunior.local",
        "https://abdullah-junior-api.fly.dev",
        "*"  # Allow all for mobile app
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount notification routes
if notifications_router:
    app.include_router(notifications_router)
    print("Mounted notifications router")
else:
    print("[API Server] Notifications router not mounted")

# ==================== Models ====================

class TaskApprovalRequest(BaseModel):
    """Request to approve or reject a task."""
    approved: bool
    note: Optional[str] = None

class DashboardData(BaseModel):
    """Dashboard summary data."""
    pending_count: int
    in_progress_count: int
    done_today_count: int
    urgent_count: int
    last_updated: str

class ChatMessage(BaseModel):
    """Chat message from user."""
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    """Response from AI agent."""
    response: str
    action_taken: Optional[str] = None
    task_created: Optional[str] = None
    suggestions: Optional[List[str]] = None

# ==================== Helper function ====================
def parse_task_metadata(content: str) -> Dict[str, Any]:
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

# ==================== Endpoints ====================

@app.get("/")
async def root():
    """API root - health check."""
    return {
        "status": "operational",
        "service": "Abdullah Junior API",
        "version": "2.0.0",
        "features": [
            "push_notifications",
            "task_management",
            "agentic_intelligence"
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "components": {
            "api": "operational",
            "vault": VAULT_PATH.exists(),
            "notifications": True
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/dashboard")
async def get_dashboard():
    """Get dashboard summary data."""
    try:
        needs_action = VAULT_PATH / "Needs_Action"
        in_progress = VAULT_PATH / "In_Progress"
        done = VAULT_PATH / "Done"
        pending_approval = VAULT_PATH / "Pending_Approval"

        # Count files
        pending = len(list(needs_action.glob("*.md"))) if needs_action.exists() else 0
        pending += len(list(pending_approval.glob("*.md"))) if pending_approval.exists() else 0

        in_prog = 0
        if in_progress.exists():
            in_prog = len(list(in_progress.glob("**/*.md")))

        # Done today
        done_today = 0
        if done.exists():
            today = datetime.now().strftime("%Y-%m-%d")
            for f in done.glob("*.md"):
                if today in f.name:
                    done_today += 1

        # Count urgent (simple heuristic)
        urgent = 0
        if needs_action.exists():
            for f in needs_action.glob("*.md"):
                content = f.read_text(encoding='utf-8', errors='replace')
                if "urgent" in content.lower() or "priority: high" in content.lower():
                    urgent += 1

        return {
            "pending_count": pending,
            "in_progress_count": in_prog,
            "done_today_count": done_today,
            "urgent_count": urgent,
            "last_updated": datetime.now().isoformat()
        }

    except Exception as e:
        print(f"Error in get_dashboard: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks")
async def get_tasks(folder: str = "Needs_Action", limit: int = 20):
    """Get tasks from a specific folder."""
    folder_path = VAULT_PATH / folder

    if not folder_path.exists():
        return {"tasks": [], "count": 0}

    tasks = []
    for f in sorted(folder_path.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)[:limit]:
        content = f.read_text(encoding='utf-8', errors='replace')
        tasks.append({
            "id": f.stem,
            "filename": f.name,
            "content_preview": content[:200] + "..." if len(content) > 200 else content,
            "created": datetime.fromtimestamp(f.stat().st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
        })

    return {"tasks": tasks, "count": len(tasks)}

@app.get("/api/tasks/pending")
async def get_pending_tasks(limit: int = 20):
    """Get pending approval tasks with full metadata."""
    pending = VAULT_PATH / "Pending_Approval"

    if not pending.exists():
        return {"tasks": [], "count": 0}

    tasks = []
    for f in sorted(pending.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)[:limit]:
        content = f.read_text(encoding='utf-8', errors='replace')
        metadata = parse_task_metadata(content)

        tasks.append({
            "id": f.stem,
            "filename": f.name,
            "title": metadata['title'],
            "description": metadata['description'],
            "priority": metadata['priority'],
            "source": metadata['source'],
            "risk_score": metadata['risk_score'],
            "complexity_score": metadata['complexity_score'],
            "created": datetime.fromtimestamp(f.stat().st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
        })

    return {"tasks": tasks, "count": len(tasks)}

print("All endpoints defined successfully!")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", 8000))
    print(f"About to start server on port {port}")
    uvicorn.run(
        "debug_api_server:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
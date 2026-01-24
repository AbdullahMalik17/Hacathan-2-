"""
Push Notification API - REST endpoints for mobile notification management.

These endpoints allow the PWA frontend to:
1. Subscribe to push notifications
2. Unsubscribe from push notifications
3. Get VAPID public key for subscription
4. Test notifications
"""

import sys
from pathlib import Path

# Ensure imports work from any location
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Any, Dict, Optional
from datetime import datetime

# Try multiple import paths for push_service
try:
    from .push_service import get_push_service, NotificationPayload
except ImportError:
    try:
        from push_service import get_push_service, NotificationPayload
    except ImportError:
        from notifications.push_service import get_push_service, NotificationPayload

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


class SubscriptionRequest(BaseModel):
    """Request to register a push subscription."""
    endpoint: str
    keys: Dict[str, str]  # Must contain p256dh and auth
    device_name: Optional[str] = None


class UnsubscribeRequest(BaseModel):
    """Request to unregister a push subscription."""
    endpoint: str


class TestNotificationRequest(BaseModel):
    """Request to send a test notification."""
    title: Optional[str] = "Test from Abdullah Junior"
    body: Optional[str] = "Push notifications are working! 🎉"


class ProactiveSuggestionRequest(BaseModel):
    """Request to send a proactive suggestion notification."""
    title: str
    description: str
    action_id: str
    priority: str = "normal"
    context: Optional[Dict[str, Any]] = None


class ApprovalRequest(BaseModel):
    """Request to send an approval notification."""
    task_id: str
    task_title: str
    task_description: str
    risk_score: float = 0.5
    complexity_score: float = 0.5


@router.get("/vapid-public-key")
async def get_vapid_public_key():
    """
    Get the VAPID public key for push subscription.

    The client needs this key to subscribe to push notifications.
    Returns the applicationServerKey for PushManager.subscribe().
    """
    push_service = get_push_service()
    public_key = push_service.get_vapid_public_key()

    if not public_key:
        raise HTTPException(
            status_code=503,
            detail="VAPID keys not configured. Set VAPID_PUBLIC_KEY environment variable."
        )

    return {"publicKey": public_key}


@router.post("/subscribe")
async def subscribe(request: SubscriptionRequest, req: Request):
    """
    Register a push subscription from a device.

    Called when user enables notifications in the PWA.
    Stores the subscription for future push notifications.
    """
    push_service = get_push_service()

    # Validate keys
    if "p256dh" not in request.keys or "auth" not in request.keys:
        raise HTTPException(
            status_code=400,
            detail="Invalid subscription: missing p256dh or auth keys"
        )

    # Get device name from user agent if not provided
    device_name = request.device_name
    if not device_name:
        user_agent = req.headers.get("user-agent", "Unknown")
        if "iPhone" in user_agent or "iPad" in user_agent:
            device_name = "iOS Device"
        elif "Android" in user_agent:
            device_name = "Android Device"
        elif "Windows" in user_agent:
            device_name = "Windows Device"
        elif "Mac" in user_agent:
            device_name = "Mac Device"
        else:
            device_name = "Unknown Device"

    success = push_service.register_subscription(
        endpoint=request.endpoint,
        keys=request.keys,
        device_name=device_name
    )

    if success:
        return {
            "success": True,
            "message": f"Subscription registered for {device_name}",
            "device_name": device_name
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to register subscription")


@router.post("/unsubscribe")
async def unsubscribe(request: UnsubscribeRequest):
    """
    Unregister a push subscription.

    Called when user disables notifications in the PWA.
    """
    push_service = get_push_service()

    success = push_service.unregister_subscription(request.endpoint)

    return {
        "success": success,
        "message": "Subscription removed" if success else "Subscription not found"
    }


@router.get("/status")
async def get_status():
    """
    Get push notification service status.

    Returns subscription counts and service health.
    """
    push_service = get_push_service()
    stats = push_service.get_subscription_count()

    return {
        "status": "operational",
        "subscriptions": stats,
        "vapid_configured": bool(push_service.get_vapid_public_key()),
        "timestamp": datetime.now().isoformat()
    }


@router.post("/test")
async def send_test_notification(request: TestNotificationRequest):
    """
    Send a test notification to all subscribed devices.

    Used to verify push notifications are working.
    """
    push_service = get_push_service()

    notification = NotificationPayload(
        title=request.title,
        body=request.body,
        tag="test-notification",
        data={"url": "/", "type": "test"},
        actions=[
            {"action": "view", "title": "Open App"}
        ]
    )

    result = await push_service.send_notification(notification)

    return {
        "success": result["sent"] > 0,
        "sent": result["sent"],
        "failed": result["failed"],
        "message": f"Test notification sent to {result['sent']} device(s)"
    }


@router.post("/send/suggestion")
async def send_suggestion(request: ProactiveSuggestionRequest):
    """
    Send a proactive suggestion notification.

    Used by the Agentic Intelligence Layer to notify
    users of opportunities or suggestions.
    """
    push_service = get_push_service()

    result = await push_service.send_proactive_suggestion(
        title=request.title,
        description=request.description,
        action_id=request.action_id,
        priority=request.priority,
        context=request.context
    )

    return {
        "success": result["sent"] > 0,
        "sent": result["sent"],
        "failed": result["failed"]
    }


@router.post("/send/approval")
async def send_approval_request(request: ApprovalRequest):
    """
    Send an approval request notification.

    Used when a task requires user approval before execution.
    """
    push_service = get_push_service()

    result = await push_service.send_approval_request(
        task_id=request.task_id,
        task_title=request.task_title,
        task_description=request.task_description,
        risk_score=request.risk_score,
        complexity_score=request.complexity_score
    )

    return {
        "success": result["sent"] > 0,
        "sent": result["sent"],
        "failed": result["failed"]
    }


@router.post("/send/digest")
async def send_daily_digest(
    summary: str,
    task_count: int = 0,
    urgent_count: int = 0,
    suggestions: list = None
):
    """
    Send daily digest notification.

    Sent each morning with a summary of pending tasks
    and proactive suggestions.
    """
    push_service = get_push_service()

    result = await push_service.send_daily_digest(
        summary=summary,
        task_count=task_count,
        urgent_count=urgent_count,
        suggestions=suggestions or []
    )

    return {
        "success": result["sent"] > 0,
        "sent": result["sent"],
        "failed": result["failed"]
    }


@router.post("/send/completed")
async def send_task_completed(
    task_id: str,
    task_title: str,
    result_summary: str
):
    """
    Send task completion notification.

    Notifies user when an approved task has been completed.
    """
    push_service = get_push_service()

    result = await push_service.send_task_completed(
        task_id=task_id,
        task_title=task_title,
        result_summary=result_summary
    )

    return {
        "success": result["sent"] > 0,
        "sent": result["sent"],
        "failed": result["failed"]
    }

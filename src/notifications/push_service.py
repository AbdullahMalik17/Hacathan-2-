"""
Push Notification Service - Send notifications to mobile devices.

This service enables Abdullah Junior to send proactive notifications
to the user's phone when the Agentic Intelligence Layer detects
opportunities or requires approval.
"""

import json
import os
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict

# Firebase Integration
try:
    from .firebase_config import init_firebase
    HAS_FIREBASE = True
except ImportError:
    HAS_FIREBASE = False
    print("[PushService] Firebase config not found.")

# Web Push library for VAPID-based push notifications
try:
    from pywebpush import webpush, WebPushException
    HAS_WEBPUSH = True
except ImportError:
    HAS_WEBPUSH = False
    print("[PushService] pywebpush not installed. Run: pip install pywebpush")


@dataclass
class PushSubscription:
    """Push subscription from a client device (Web or Mobile)."""
    endpoint: str  # For Web Push: URL, For Mobile: FCM Token
    keys: Dict[str, str] = field(default_factory=dict) # For Web Push only
    device_name: str = "Unknown Device"
    platform: str = "web"  # web, android, ios
    created_at: datetime = field(default_factory=datetime.now)
    last_used: datetime = field(default_factory=datetime.now)
    is_active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "endpoint": self.endpoint,
            "keys": self.keys,
            "device_name": self.device_name,
            "platform": self.platform,
            "created_at": self.created_at.isoformat(),
            "last_used": self.last_used.isoformat(),
            "is_active": self.is_active
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PushSubscription":
        return cls(
            endpoint=data["endpoint"],
            keys=data.get("keys", {}),
            device_name=data.get("device_name", "Unknown Device"),
            platform=data.get("platform", "web"),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            last_used=datetime.fromisoformat(data.get("last_used", datetime.now().isoformat())),
            is_active=data.get("is_active", True)
        )


@dataclass
class NotificationPayload:
    """Notification payload to send to device."""
    title: str
    body: str
    icon: str = "/icons/icon-192x192.png"
    badge: str = "/icons/badge-72.png"
    tag: str = "default"
    data: Dict[str, Any] = field(default_factory=dict)
    actions: List[Dict[str, str]] = field(default_factory=list)
    require_interaction: bool = False
    priority: str = "normal"  # low, normal, high, urgent

    def to_json(self) -> str:
        return json.dumps({
            "title": self.title,
            "body": self.body,
            "icon": self.icon,
            "badge": self.badge,
            "tag": self.tag,
            "data": self.data,
            "actions": self.actions,
            "requireInteraction": self.require_interaction
        })


class PushNotificationService:
    """
    Service to send push notifications to registered devices.
    Supports Web Push (VAPID) and Firebase Cloud Messaging (Mobile).
    """

    def __init__(self, config_dir: str = None):
        """
        Initialize the push notification service.

        Args:
            config_dir: Directory for storing subscriptions and VAPID keys
        """
        self.config_dir = Path(config_dir or os.getenv(
            "PUSH_CONFIG_DIR",
            "config/push_notifications"
        ))
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.subscriptions_file = self.config_dir / "subscriptions.json"
        self.vapid_file = self.config_dir / "vapid_keys.json"

        # Load or generate VAPID keys (for Web Push)
        self.vapid_claims = self._load_vapid_keys()

        # Load existing subscriptions
        self.subscriptions: List[PushSubscription] = self._load_subscriptions()

        # Initialize Firebase
        if HAS_FIREBASE:
            self.firebase_ready = init_firebase()
        else:
            self.firebase_ready = False

        print(f"[PushService] Initialized with {len(self.subscriptions)} subscription(s)")

    def _load_vapid_keys(self) -> Dict[str, str]:
        """Load or generate VAPID keys for push authentication."""
        if self.vapid_file.exists():
            with open(self.vapid_file) as f:
                return json.load(f)

        # Generate new VAPID keys if not exists
        vapid_claims = {
            "sub": os.getenv("VAPID_SUBJECT", "mailto:admin@abdullahjunior.local"),
            "private_key": os.getenv("VAPID_PRIVATE_KEY", ""),
            "public_key": os.getenv("VAPID_PUBLIC_KEY", "")
        }

        # Save for future use
        with open(self.vapid_file, "w") as f:
            json.dump(vapid_claims, f, indent=2)

        return vapid_claims

    def _load_subscriptions(self) -> List[PushSubscription]:
        """Load existing push subscriptions from storage."""
        if not self.subscriptions_file.exists():
            return []

        try:
            with open(self.subscriptions_file) as f:
                data = json.load(f)
                return [PushSubscription.from_dict(s) for s in data]
        except Exception as e:
            print(f"[PushService] Error loading subscriptions: {e}")
            return []

    def _save_subscriptions(self):
        """Save subscriptions to storage."""
        with open(self.subscriptions_file, "w") as f:
            json.dump([s.to_dict() for s in self.subscriptions], f, indent=2)

    def register_subscription(
        self,
        endpoint: str,
        keys: Dict[str, str] = None,
        device_name: str = "Unknown Device",
        platform: str = "web"
    ) -> bool:
        """
        Register a new push subscription.

        Args:
            endpoint: Push service endpoint URL (Web) or FCM Token (Mobile)
            keys: p256dh and auth keys (Web only)
            device_name: Friendly name for the device
            platform: web, android, ios

        Returns:
            True if subscription was registered successfully
        """
        # Check if already exists (by endpoint)
        for sub in self.subscriptions:
            if sub.endpoint == endpoint:
                sub.is_active = True
                sub.last_used = datetime.now()
                sub.device_name = device_name
                sub.platform = platform
                self._save_subscriptions()
                print(f"[PushService] Updated existing subscription: {device_name} ({platform})")
                return True

        # Add new subscription
        subscription = PushSubscription(
            endpoint=endpoint,
            keys=keys or {},
            device_name=device_name,
            platform=platform
        )
        self.subscriptions.append(subscription)
        self._save_subscriptions()

        print(f"[PushService] Registered new subscription: {device_name} ({platform})")
        return True

    def unregister_subscription(self, endpoint: str) -> bool:
        """Unregister a push subscription."""
        for sub in self.subscriptions:
            if sub.endpoint == endpoint:
                sub.is_active = False
                self._save_subscriptions()
                print(f"[PushService] Unregistered subscription: {sub.device_name}")
                return True
        return False

    async def send_fcm_notification(
        self,
        fcm_token: str,
        notification: NotificationPayload,
        platform: str = "android"
    ) -> Dict[str, Any]:
        """Send notification via Firebase Cloud Messaging."""
        if not self.firebase_ready:
            return {"success": False, "error": "Firebase not initialized"}

        try:
            from firebase_admin import messaging

            # Construct message
            # Note: We send 'data' payload primarily for flexibility
            message = messaging.Message(
                notification=messaging.Notification(
                    title=notification.title,
                    body=notification.body,
                ),
                data={k: str(v) for k, v in (notification.data or {}).items()},
                token=fcm_token,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        icon='notification_icon',
                        color='#2563eb',
                        channel_id='approvals' if 'approval' in notification.tag else 'default',
                        tag=notification.tag
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            alert=messaging.ApsAlert(
                                title=notification.title,
                                body=notification.body,
                            ),
                            badge=1,
                            sound='default',
                        )
                    )
                )
            )

            response = messaging.send(message)
            return {"success": True, "message_id": response}

        except Exception as e:
            print(f"[PushService] FCM send failed: {e}")
            return {"success": False, "error": str(e)}

    async def send_notification(
        self,
        notification: NotificationPayload,
        device_name: str = None
    ) -> Dict[str, Any]:
        """
        Send a push notification to registered devices.
        
        Args:
            notification: The notification payload to send
            device_name: Optional specific device to target

        Returns:
            Dict with success/failure counts
        """
        active_subs = [s for s in self.subscriptions if s.is_active]

        if device_name:
            active_subs = [s for s in active_subs if s.device_name == device_name]

        if not active_subs:
            print("[PushService] No active subscriptions to notify")
            return {"sent": 0, "failed": 0, "reason": "No active subscriptions"}

        results = {"sent": 0, "failed": 0, "errors": []}

        for sub in active_subs:
            try:
                if sub.platform == 'web':
                    # Send via Web Push (VAPID)
                    if HAS_WEBPUSH and self.vapid_claims.get("private_key"):
                        webpush(
                            subscription_info={
                                "endpoint": sub.endpoint,
                                "keys": sub.keys
                            },
                            data=notification.to_json(),
                            vapid_private_key=self.vapid_claims["private_key"],
                            vapid_claims={"sub": self.vapid_claims["sub"]}
                        )
                        sub.last_used = datetime.now()
                        results["sent"] += 1
                        print(f"[PushService] Sent Web Push to {sub.device_name}")
                    else:
                        print(f"[PushService] Skipping Web Push to {sub.device_name} (No VAPID)")

                elif sub.platform in ['android', 'ios']:
                    # Send via FCM
                    if self.firebase_ready:
                        res = await self.send_fcm_notification(sub.endpoint, notification, sub.platform)
                        if res.get("success"):
                            sub.last_used = datetime.now()
                            results["sent"] += 1
                            print(f"[PushService] Sent FCM to {sub.device_name}")
                        else:
                            results["failed"] += 1
                            results["errors"].append(res.get("error"))
                            # Check if token is invalid (TODO: improved error checking)
                            print(f"[PushService] Failed FCM to {sub.device_name}: {res.get('error')}")
                    else:
                        print(f"[PushService] Skipping FCM to {sub.device_name} (Firebase not ready)")

            except Exception as e:
                results["failed"] += 1
                results["errors"].append(str(e))
                
                # Handle Web Push 410/404
                if hasattr(e, 'response') and e.response and e.response.status_code in [404, 410]:
                    sub.is_active = False
                    print(f"[PushService] Web Push Subscription expired: {sub.device_name}")
                else:
                    print(f"[PushService] Failed to send to {sub.device_name}: {e}")

        self._save_subscriptions()
        return results

    async def send_proactive_suggestion(
        self,
        title: str,
        description: str,
        action_id: str,
        priority: str = "normal",
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Send a proactive suggestion notification."""
        # Determine actions based on priority
        if priority in ["high", "urgent"]:
            actions = [
                {"action": "approve", "title": "✓ Do it"},
                {"action": "view", "title": "Review"},
                {"action": "dismiss", "title": "Later"}
            ]
            require_interaction = True
        else:
            actions = [
                {"action": "view", "title": "View"},
                {"action": "dismiss", "title": "Dismiss"}
            ]
            require_interaction = False

        notification = NotificationPayload(
            title=f"💡 {title}",
            body=description,
            tag=f"suggestion-{action_id}",
            data={
                "url": f"/?action={action_id}",
                "actionId": action_id,
                "type": "proactive_suggestion",
                **(context or {})
            },
            actions=actions,
            require_interaction=require_interaction,
            priority=priority
        )

        return await self.send_notification(notification)

    async def send_approval_request(
        self,
        task_id: str,
        task_title: str,
        task_description: str,
        risk_score: float = 0.5,
        complexity_score: float = 0.5
    ) -> Dict[str, Any]:
        """Send an approval request notification for a task."""
        # Determine urgency indicator
        if risk_score >= 0.7:
            icon_prefix = "🔴"
            require_interaction = True
        elif risk_score >= 0.4:
            icon_prefix = "🟡"
            require_interaction = True
        else:
            icon_prefix = "🟢"
            require_interaction = False

        notification = NotificationPayload(
            title=f"{icon_prefix} Approval Needed: {task_title}",
            body=task_description[:200] + ("..." if len(task_description) > 200 else ""),
            tag=f"approval-{task_id}",
            data={
                "url": f"/?task={task_id}&action=approve",
                "taskId": task_id,
                "type": "approval_request",
                "riskScore": risk_score,
                "complexityScore": complexity_score
            },
            actions=[
                {"action": "approve", "title": "✓ Approve"},
                {"action": "reject", "title": "✗ Reject"},
                {"action": "view", "title": "Review Details"}
            ],
            require_interaction=require_interaction,
            priority="high" if risk_score >= 0.5 else "normal"
        )

        return await self.send_notification(notification)

    async def send_daily_digest(
        self,
        summary: str,
        task_count: int,
        urgent_count: int,
        suggestions: List[str]
    ) -> Dict[str, Any]:
        """Send daily morning digest notification."""
        body_parts = [summary]
        if urgent_count > 0:
            body_parts.append(f"🔴 {urgent_count} urgent item(s)")
        if task_count > 0:
            body_parts.append(f"📋 {task_count} pending task(s)")

        notification = NotificationPayload(
            title="☀️ Good Morning! Your Daily Briefing",
            body=" | ".join(body_parts),
            tag="daily-digest",
            data={
                "url": "/?view=digest",
                "type": "daily_digest",
                "taskCount": task_count,
                "urgentCount": urgent_count,
                "suggestions": suggestions[:5]  # Top 5 suggestions
            },
            actions=[
                {"action": "view", "title": "View Full Briefing"},
                {"action": "dismiss", "title": "Later"}
            ],
            require_interaction=False,
            priority="normal"
        )

        return await self.send_notification(notification)

    async def send_task_completed(
        self,
        task_id: str,
        task_title: str,
        result_summary: str
    ) -> Dict[str, Any]:
        """Notify user that a task was completed."""
        notification = NotificationPayload(
            title=f"✅ Completed: {task_title}",
            body=result_summary,
            tag=f"completed-{task_id}",
            data={
                "url": f"/?task={task_id}",
                "taskId": task_id,
                "type": "task_completed"
            },
            actions=[
                {"action": "view", "title": "View Result"}
            ],
            require_interaction=False,
            priority="low"
        )

        return await self.send_notification(notification)

    def get_vapid_public_key(self) -> str:
        """Get the VAPID public key for client subscription."""
        return self.vapid_claims.get("public_key", "")

    def get_subscription_count(self) -> Dict[str, int]:
        """Get subscription statistics."""
        active = sum(1 for s in self.subscriptions if s.is_active)
        return {
            "total": len(self.subscriptions),
            "active": active,
            "inactive": len(self.subscriptions) - active
        }


# Singleton instance
_push_service: Optional[PushNotificationService] = None


def get_push_service() -> PushNotificationService:
    """Get the singleton push notification service instance."""
    global _push_service
    if _push_service is None:
        _push_service = PushNotificationService()
    return _push_service
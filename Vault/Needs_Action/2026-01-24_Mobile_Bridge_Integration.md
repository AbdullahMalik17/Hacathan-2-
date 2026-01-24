# Task: Implement Mobile Bridge Integration

**Priority:** High
**Domain:** Mobile Control
**Assigned To:** Gemini Agent
**Created:** 2026-01-24

---

## Objective

Create a Mobile Bridge system that connects Abdullah Junior to the user's Android/iOS phone for:
1. **Location awareness** - Know when user arrives/leaves locations
2. **Notification relay** - Forward important notifications to the agent
3. **Device control** - Trigger actions on the phone (DND mode, volume, etc.)

---

## Requirements

### 1. Mobile App / Tasker Integration

Create integration with **Tasker** (Android) or **Shortcuts** (iOS) to:

- Send location updates to the API server
- Forward notifications matching specific criteria
- Execute commands from the agent (set volume, DND, etc.)

### 2. API Endpoints Needed

Create these endpoints in `src/api_server.py`:

```python
POST /api/mobile/location
# Receive location updates from phone
# Body: {"lat": float, "lon": float, "location_name": str, "timestamp": str}

POST /api/mobile/notification
# Receive forwarded notifications
# Body: {"app": str, "title": str, "content": str, "timestamp": str}

POST /api/mobile/status
# Receive device status updates
# Body: {"battery": int, "charging": bool, "network": str, "dnd": bool}

GET /api/mobile/commands
# Phone polls for pending commands
# Returns: {"commands": [{"action": "set_dnd", "value": true}, ...]}

POST /api/mobile/command/{id}/complete
# Phone confirms command execution
```

### 3. Location Intelligence

Create `src/intelligence/location_monitor.py`:

```python
class LocationMonitor:
    """Monitor location and trigger context-aware actions."""

    # Define known locations
    LOCATIONS = {
        "home": {"lat": ..., "lon": ..., "radius": 100},
        "office": {"lat": ..., "lon": ..., "radius": 200},
        "gym": {"lat": ..., "lon": ..., "radius": 50}
    }

    async def on_location_update(self, lat, lon):
        """Handle location update from phone."""
        location = self.identify_location(lat, lon)

        if location == "office" and self.previous != "office":
            await self.on_arrive_office()
        elif location == "home" and self.previous != "home":
            await self.on_arrive_home()

    async def on_arrive_office(self):
        """Trigger work mode."""
        # Play focus music
        # Set DND on phone
        # Show daily tasks

    async def on_arrive_home(self):
        """Trigger home mode."""
        # Stop work notifications
        # Relax music
```

### 4. Tasker Profile Export

Create a Tasker profile that the user can import:

```
Profile: Abdullah Junior Bridge

Task: Send Location
    Trigger: Location change
    Action: HTTP POST to http://PC_IP:8000/api/mobile/location
    Body: {"lat": %LOC_LAT, "lon": %LOC_LON, "timestamp": %TIMES}

Task: Forward Notification
    Trigger: Notification from Gmail, WhatsApp, Slack
    Action: HTTP POST to http://PC_IP:8000/api/mobile/notification
    Body: {"app": %NTITLE, "title": %TITLE, "content": %SMSRB}

Task: Check Commands
    Trigger: Every 5 minutes
    Action: HTTP GET http://PC_IP:8000/api/mobile/commands
    If commands exist: Execute them
```

---

## Files to Create

1. `src/mobile/bridge.py` - Main mobile bridge service
2. `src/mobile/location_monitor.py` - Location-aware actions
3. `src/mobile/commands.py` - Command queue for phone
4. `src/mobile/__init__.py` - Module exports
5. `config/mobile_config.json` - Known locations, settings
6. `docs/MOBILE_BRIDGE_SETUP.md` - Setup instructions with Tasker

---

## Acceptance Criteria

- [ ] API endpoints accept location updates from phone
- [ ] Location changes trigger context-aware actions
- [ ] Notifications from phone are forwarded to agent
- [ ] Agent can send commands to phone (DND, etc.)
- [ ] Tasker profile documented for easy setup
- [ ] Works over local network (no cloud required)

---

## Notes

- Use local network only (privacy first)
- Phone should poll for commands (not push)
- Store location history for pattern learning
- Integrate with Context Monitor for proactive suggestions

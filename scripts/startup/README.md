# Digital FTE Auto-Start Setup

This folder contains scripts to configure Digital FTE to start automatically when you log into your Windows laptop.

## Quick Setup

### Install Auto-Start

1. Open PowerShell as **Administrator**
2. Navigate to this directory:
   ```powershell
   cd D:\Hacathan_2\scripts\startup
   ```
3. Run the installation script:
   ```powershell
   .\install_autostart.ps1
   ```

### What Gets Installed

The script creates two Windows Task Scheduler entries:

1. **DigitalFTE_AutoStart** - Runs at user login
   - Starts Gmail Watcher
   - Starts Filesystem Watcher
   - Starts WhatsApp Watcher (requires manual QR scan first time)
   - Starts Orchestrator

2. **DigitalFTE_WeeklyBriefing** - Runs every Monday at 8:00 AM
   - Generates CEO Briefing report
   - Saves to `Vault/CEO_Briefing_YYYY-MM-DD.md`

### Uninstall Auto-Start

To remove auto-start:

```powershell
.\install_autostart.ps1 -Uninstall
```

### Reinstall (Force)

To reinstall if tasks already exist:

```powershell
.\install_autostart.ps1 -Force
```

## Manual Testing

To test the startup script without rebooting:

```batch
start_digital_fte.bat
```

## Logs

- Installation log: `Vault/Logs/autostart_install.log`
- Startup events: `Vault/Logs/startup_log.md`
- Service status: `Vault/Logs/startup.log`

## Troubleshooting

### Services not starting

1. Check `Vault/Logs/startup_log.md` for errors
2. Verify Python is in your PATH
3. Ensure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

### WhatsApp Watcher needs authentication

WhatsApp Web requires a QR code scan on first run:
1. Run `python src/watchers/whatsapp_watcher.py` manually
2. Scan the QR code with your phone
3. The session will be saved for future auto-starts

### Gmail Watcher authentication error

Re-run the Gmail setup:
```bash
python src/watchers/setup_auth.py
```

## Components Started

| Service | Description | Restart Delay |
|---------|-------------|---------------|
| Gmail Watcher | Monitors inbox for new emails | 5 seconds |
| Filesystem Watcher | Monitors DropFolder for new files | 5 seconds |
| WhatsApp Watcher | Monitors WhatsApp Web for messages | 10 seconds |
| Orchestrator | Processes tasks with Ralph Wiggum loop | 5 seconds |

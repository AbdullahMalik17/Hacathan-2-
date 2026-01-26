# Abdullah Junior: The Elite Digital FTE (Full-Time Equivalent)

**"Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop."**

Abdullah Junior is a high-autonomy AI agent system designed for the 2026 Personal AI Employee Hackathon. It proactively manages personal and business affairs 24/7 using a sophisticated multi-agent architecture.

## 🚀 Elite Platinum Tier Features

- **Multi-Agent Swarm:** Specialized agent personas (Strategist, Communicator, Auditor) collaborate on complex tasks.
- **Self-Healing Logic:** A "Guardian" system that detects script crashes, asks the AI for fixes, and recovers automatically.
- **Sentiment-Aware Triage:** Intelligent Gmail monitoring that detects "Angry" or "Urgent" tones and escalates priority instantly.
- **Voice-First Interface:** Mobile-integrated voice transcription for hands-free agent control.
- **Always-On Cloud + Local Executive:** Hybrid deployment on Fly.io (Cloud) and Local machine with synced Obsidian Vault.
- **Mobile Companion App:** React Native (Expo) dashboard for real-time approvals and agent chat.
- **Autonomous Business Audit:** Weekly "Monday Morning CEO Briefings" with revenue analysis and bottleneck detection.

## 🛠 Tech Stack

- **Reasoning Engine:** Gemini Pro / Claude 3.5 via Agentic Orchestrator.
- **Memory/GUI:** Obsidian (Local Markdown) & Next.js Web Dashboard.
- **Mobile:** React Native (Expo) with FCM Push Notifications.
- **Cloud:** Fly.io (Backend/Watchers) & Vercel (Frontend).
- **Integrations:** Gmail API, LinkedIn, Odoo Community (Accounting), WhatsApp.

## 📦 Deployment

### Cloud Backend (Fly.io)
```bash
# Deploys API, Orchestrator, and Watchers managed by Supervisor
fly deploy
```

### Web Dashboard (Vercel)
1. Link the `frontend/` directory to Vercel.
2. Set `NEXT_PUBLIC_API_BASE_URL` to your Fly.io URL.

### Mobile App (EAS)
```bash
cd mobile
eas build --profile preview --platform android
```

## 📂 Project Structure

- `src/orchestrator.py`: The system "Brain" and task dispatcher.
- `src/watchers/`: "Senses" monitoring Gmail and system events.
- `src/intelligence/`: Swarm management and agentic decision logic.
- `src/utils/self_healer.py`: The system "Guardian" for autonomous recovery.
- `Vault/`: The "Long-term Memory" where all tasks and logs reside.

---
*Built for the 2026 AI Employee Hackathon. Autonomous. Secure. Local-First.*

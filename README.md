# Digital FTE - Personal AI Employee

> **Your autonomous 24/7 digital worker that perceives, reasons, and acts.**

![Status](https://img.shields.io/badge/Status-Bronze%20Tier%20Complete-success)
![Specs](https://img.shields.io/badge/Specs-Silver%20Tier%20Delivered-blue)
![Python](https://img.shields.io/badge/Python-3.10+-yellow)

**Digital FTE** is an autonomous agentic system designed to handle personal and business operations. Unlike standard chatbots, it runs continuously in the background using a "Watcher-Reasoner-Action" loop to monitor your digital life (Email, Files, Messaging) and take intelligent actions based on your **Company Handbook**.

---

## 🏗️ Architecture

The system follows the **Ralph Wiggum Loop** pattern for continuous autonomous operation:

```mermaid
graph TD
    subgraph Perception ["👀 Perception (Watchers)"]
        Gmail[Gmail Watcher]
        File[Filesystem Watcher]
        WA[WhatsApp Watcher]
    end

    subgraph Memory ["🧠 Local Knowledge (Obsidian)"]
        Vault[Vault Storage]
        Inbox[/Vault/Inbox]
        Needs[/Vault/Needs_Action]
        Logs[/Vault/Logs]
    end

    subgraph Reasoning ["🤔 Reasoning Engine"]
        Orchestrator[Orchestrator]
        Claude[Claude Code / LLM]
    end

    subgraph Action ["⚡ Action Layer"]
        Approve{Human Review?}
        Exec[Execute Action]
        MCP[MCP Servers]
        EmailSender[Email Sender Tool]
    end

    Gmail --> Inbox
    File --> Inbox
    WA --> Inbox
    
    Inbox --> Orchestrator
    Orchestrator --> Claude
    Claude -- "Consults" --> Vault
    Claude --> Needs
    
    Needs --> Approve
    Approve -- "Auto-Approve" --> Exec
    Approve -- "Risk > Threshold" --> Needs
    
    Exec --> MCP
    MCP --> EmailSender
    MCP --> Logs
```

### Core Components
1.  **Service Manager**: Daemon that keeps all watchers and the orchestrator running (`src/service_manager.py`).
2.  **Watchers**: Python scripts that poll external sources and create markdown tasks in the Vault.
3.  **Orchestrator**: The main loop that processes tasks from `Needs_Action` using AI.
4.  **Vault**: An Obsidian-compatible folder structure acting as the agent's long-term memory and UI.

---

## ✨ Capabilities & Features

### 🥉 Bronze Tier (Live)
*   **Centralized Control**: `Service Manager` handles startup and crash recovery for all agents.
*   **Gmail Monitoring**: `Gmail Watcher` polls inbox for high-priority emails.
*   **Contextual Intelligence**: Actions are governed by `Vault/Company_Handbook.md`.
*   **Human-in-the-loop**: High-risk actions (e.g., sending emails to new contacts) wait for your approval in `Vault/Pending_Approval`.
*   **Audit Logging**: Every action is cryptographically logged in `Vault/Logs/`.
*   **Email MCP**: Tool for agents to send emails safely.

### 🥈 Silver Tier (Specified & Ready to Build)
*   **WhatsApp Integration**: Watcher for processing WhatsApp messages.
*   **Filesystem Watcher**: "Drop folder" automation for document processing.
*   **CEO Briefing**: Weekly autonomous report generation on agent activities.
*   **Laptop Startup**: Auto-boot scripts to launch Digital FTE on login.

> *Silver Tier specifications are available in `specs/` directory.*

---

## 📂 Project Structure

```text
Hacathan_2/
├── 📋 specs/                   # SpecifyPlus Feature Specifications
│   ├── 001-laptop-startup-spec.md
│   ├── 002-email-sender-mcp-spec.md
│   └── ...
├── 🛠️ src/                     # Source Code
│   ├── mcp_servers/            # Model Context Protocol Servers
│   ├── watchers/               # Perception Agents (Gmail, Filesystem)
│   ├── reports/                # Report Generators
│   ├── orchestrator.py         # Main Reasoning Loop
│   └── service_manager.py      # System Daemon
├── 🧠 Vault/                   # Obsidian Knowledge Base
│   ├── Inbox/                  # Raw incoming signals
│   ├── Needs_Action/           # Tasks awaiting AI processing
│   ├── Pending_Approval/       # Tasks awaiting Human review
│   ├── Approved/               # Tasks authorized for execution
│   └── Logs/                   # System operation logs
├── ⚙️ config/                  # Configuration & Env Vars
└── 📄 README.md                # This file
```

---

## 🚀 Getting Started

### Prerequisites
*   Python 3.10+
*   Google Cloud Project (for Gmail API)
*   User account for WhatsApp (optional)

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/AbdullahMalik17/Hacathan-2-.git
    cd Hacathan-2-
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment**
    ```bash
    cp config/.env.example config/.env
    # Edit config/.env with your API keys
    ```
    *Place `credentials.json` from Google Cloud in `config/`.*

### Running the System

Start the full system (Watchers + Orchestrator) with the Service Manager:

```bash
python src/service_manager.py
```

*The Service Manager will:*
*   *Start the Gmail Watcher*
*   *Start the Orchestrator*
*   *Monitor processes and auto-restart crashes*
*   *Log system health to `Vault/Logs/startup_log.md`*

---

## 📚 Documentation

*   **[Quick Start Guide](QUICK_START.md)**: How to use the specifications.
*   **[Specs Index](SPECS_INDEX.md)**: Master list of all features.
*   **[Company Handbook](Vault/Company_Handbook.md)**: Rules governing the AI's behavior.

---

## 🤝 Contributing

We follow a **Specification-Driven Development** workflow:
1.  Read the relevant `specs/*.md` file.
2.  Generate an implementation plan (`/sp.plan`).
3.  Implement features using TDD.
4.  Submit PR.

## License

MIT License.

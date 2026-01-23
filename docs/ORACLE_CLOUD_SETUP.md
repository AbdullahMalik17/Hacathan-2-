# Oracle Cloud Setup & Survival Guide

**Objective:** Provision an Always Free Oracle Cloud Infrastructure (OCI) VM for the Digital FTE Cloud Agent.

## 1. The Challenge: "Sign-Up/In Error"

Oracle Cloud sign-up is notoriously strict to prevent abuse. If you are stuck at the sign-in/sign-up page with errors, try these proven solutions:

### Troubleshooting Sign-In/Up

1.  **Browser Issues:**
    *   **Disable Ad Blockers:** Oracle's fraud detection scripts often get blocked.
    *   **Use Incognito/Private Mode:** Clears potentially conflicting cache/cookies.
    *   **Try a Different Browser:** If Chrome fails, try Firefox or Edge.

2.  **Credit Card / Identity Verification:**
    *   **Address Match:** Ensure your billing address matches *exactly* what is on file with your bank (abbreviations, spacing).
    *   **Pre-paid Cards:** Usually rejected. Use a standard credit/debit card.
    *   **Previous Attempts:** If you failed once, use a *different email* and *phone number*. Oracle "blacklists" failed identifiers quickly.

3.  **Region Selection:**
    *   **Home Region:** Choose a region geographically close to you.
    *   **Capacity:** Some popular regions (e.g., Ashburn, Frankfurt) run out of "Always Free" ARM instances. **Recommendation:** Try slightly less busy regions like **Phoenix**, **London**, or **Amsterdam**.

4.  **"Account creation failed" or "Error processing transaction":**
    *   Wait 24 hours before retrying with the same details.
    *   Contact Oracle Support Chat (available on the sign-up page). They are surprisingly helpful for account activation.

---

## 2. Setting Up the VM (Once You Are In)

Once you access the console (https://cloud.oracle.com), follow these steps to create your Digital FTE server.

### Step 1: Create Instance
1.  Go to **Compute** -> **Instances**.
2.  Click **Create Instance**.
3.  **Name:** `digital-fte-cloud`
4.  **Image:** Ubuntu 24.04 (or 22.04) Minimal.
5.  **Shape (Crucial):**
    *   Click **Change Shape**.
    *   Select **Ampere** (ARM) series -> **VM.Standard.A1.Flex**.
    *   **OCPUs:** 4
    *   **Memory:** 24 GB
    *   *Note: This is the high-performance "Always Free" tier.*

### Step 2: Networking
1.  **Primary Network:** Create new VCN (Virtual Cloud Network).
2.  **Subnet:** Create new public subnet.
3.  **Assign Public IPv4 Address:** Yes.

### Step 3: SSH Keys (Don't Skip!)
1.  **Add SSH Keys:** Select **"Generate a key pair for me"**.
2.  **Download Private Key:** Click **Save Private Key**.
    *   *Save this file safely! You cannot retrieve it later.*
    *   Rename it to `oracle_key.pem`.

### Step 4: Create
1.  Click **Create**.
2.  Wait for the instance to turn **Green (Running)**.
3.  Copy the **Public IP Address** (e.g., `123.45.67.89`).

---

## 3. Post-Creation Configuration

### Step 1: Open Firewall Ports (Ingress Rules)
By default, only SSH (22) is open.
1.  Click on your instance name.
2.  Click the **Subnet** link (e.g., `subnet-20260123...`).
3.  Click the **Security List** (Default Security List).
4.  Click **Add Ingress Rules**.
    *   **Source CIDR:** `0.0.0.0/0`
    *   **IP Protocol:** TCP
    *   **Destination Port Range:** `80, 443, 8069` (for Odoo/Web)
5.  Click **Add Ingress Rules**.

### Step 2: Connect via SSH
From your local terminal (Git Bash or PowerShell):

1.  **Restrict Key Permissions (Linux/Mac/Git Bash):**
    ```bash
    chmod 400 path/to/oracle_key.pem
    ```
    *(Windows PowerShell users might need to use `properties -> security` to remove access for other users)*

2.  **Connect:**
    ```bash
    ssh -i path/to/oracle_key.pem ubuntu@<YOUR_PUBLIC_IP>
    ```

---

## 4. Deploying Digital FTE

Once connected, you can use the automated script:

1.  **Upload Script (Local Terminal):**
    ```bash
    scp -i path/to/oracle_key.pem scripts/setup_cloud_vm.sh ubuntu@<YOUR_PUBLIC_IP>:~/
    ```

2.  **Run Script (SSH Session):**
    ```bash
    chmod +x setup_cloud_vm.sh
    ./setup_cloud_vm.sh
    ```

---

## 5. Alternative: Simulation (Plan B)

If Oracle Cloud remains blocked, you can simulate the Cloud Agent locally.

1.  **Open a New Terminal** (This will be your "Cloud" machine).
2.  **Configure Environment:**
    ```bash
    # Windows PowerShell
    $env:WORK_ZONE="cloud"
    python src/orchestrator.py
    ```
3.  **Run Local Agent** in your main terminal:
    ```bash
    # Windows PowerShell
    $env:WORK_ZONE="local"
    python src/orchestrator.py
    ```

This allows you to test the **Dual-Agent Interaction** (Draft -> Approval -> Execution) without a physical cloud server.

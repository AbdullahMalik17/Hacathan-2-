#!/bin/bash

# setup_cloud_vm.sh
# Automates the deployment of the Digital FTE Cloud Agent on an Ubuntu VM (e.g., Oracle Cloud).
# Usage: ./setup_cloud_vm.sh

set -e  # Exit on error

# Configuration
REPO_URL="https://github.com/AbdullahMalik17/Hacathan-2-.git"
INSTALL_DIR="$HOME/Hacathan_2"
SERVICE_NAME="digitalfte-cloud"
PYTHON_VERSION="python3"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Digital FTE Cloud Agent Setup ===${NC}"

# 1. System Updates
echo -e "${YELLOW}Step 1: Updating system packages...${NC}"
sudo apt-get update
sudo apt-get install -y git $PYTHON_VERSION-venv $PYTHON_VERSION-pip acl

# 2. Clone/Update Repository
echo -e "${YELLOW}Step 2: Setting up repository...${NC}"
if [ -d "$INSTALL_DIR" ]; then
    echo "Directory exists. Pulling latest changes..."
    cd "$INSTALL_DIR"
    git pull origin main
else
    echo "Cloning repository..."
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# 3. Virtual Environment
echo -e "${YELLOW}Step 3: Setting up Python environment...${NC}"
if [ ! -d ".venv" ]; then
    $PYTHON_VERSION -m venv .venv
fi

source .venv/bin/activate
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Configuration
echo -e "${YELLOW}Step 4: Configuring environment...${NC}"
if [ ! -f ".env" ]; then
    if [ -f "config/.env.cloud.example" ]; then
        cp config/.env.cloud.example .env
        echo -e "${GREEN}Created .env from cloud template.${NC}"
    else
        echo -e "${RED}Warning: config/.env.cloud.example not found. Creating empty .env.${NC}"
        touch .env
    fi
    echo -e "${YELLOW}IMPORTANT: You must edit $INSTALL_DIR/.env to add your credentials!${NC}"
else
    echo ".env already exists. Skipping creation."
fi

# 5. Permissions
echo -e "${YELLOW}Step 5: Setting permissions...${NC}"
# Ensure the user owns the directory
sudo chown -R $USER:$USER "$INSTALL_DIR"
# Make scripts executable
chmod +x "$INSTALL_DIR/scripts/"*.py 2>/dev/null || true
chmod +x "$INSTALL_DIR/"*.sh 2>/dev/null || true

# 6. Systemd Service
echo -e "${YELLOW}Step 6: Creating systemd service...${NC}"
SERVICE_FILE="/tmp/$SERVICE_NAME.service"

cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=Digital FTE Cloud Agent
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/.venv/bin/python $INSTALL_DIR/src/orchestrator.py
Environment="WORK_ZONE=cloud"
Environment="PYTHONUNBUFFERED=1"
# Add any other required env vars here or load from .env if supported by app logic
# EnvironmentFile=$INSTALL_DIR/.env 

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "Installing service file to /etc/systemd/system/..."
sudo mv "$SERVICE_FILE" "/etc/systemd/system/$SERVICE_NAME.service"
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"

echo -e "${GREEN}=== Setup Complete ===${NC}"
echo ""
echo "Next Steps:"
echo "1. Edit your configuration file:"
echo "   nano $INSTALL_DIR/.env"
echo ""
echo "2. Start the service:"
echo "   sudo systemctl start $SERVICE_NAME"
echo ""
echo "3. Check logs:"
echo "   sudo journalctl -u $SERVICE_NAME -f"
echo ""

#!/bin/bash
# =============================================================================
# Server Setup Script for Hetzner
# Run this script ONCE on your new Hetzner server to set up the environment
# Usage: bash setup-server.sh
# =============================================================================

set -e  # Exit on error

echo "🚀 Starting Axon Server Setup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

echo -e "${YELLOW}📦 Updating system packages...${NC}"
apt update && apt upgrade -y

echo -e "${YELLOW}🐳 Installing Docker...${NC}"
# Remove old versions
apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# Install prerequisites
apt install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    ufw

# Add Docker's official GPG key
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

# Set up repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start and enable Docker
systemctl start docker
systemctl enable docker

echo -e "${YELLOW}🔥 Configuring firewall...${NC}"
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw --force enable

echo -e "${YELLOW}📁 Creating application directory...${NC}"
mkdir -p /opt/axon
cd /opt/axon

echo -e "${YELLOW}🔑 Setting up deploy user...${NC}"
# Create deploy user if it doesn't exist
if ! id "deploy" &>/dev/null; then
    useradd -m -s /bin/bash -G docker deploy
    echo -e "${GREEN}Created 'deploy' user${NC}"
else
    usermod -aG docker deploy
    echo -e "${GREEN}'deploy' user already exists, added to docker group${NC}"
fi

# Set ownership
chown -R deploy:deploy /opt/axon

echo ""
echo -e "${GREEN}✅ Server setup complete!${NC}"
echo ""
echo -e "${YELLOW}📋 Next steps:${NC}"
echo "1. Clone your repository:"
echo "   cd /opt/axon && git clone https://github.com/YOUR_USERNAME/Axon.git ."
echo ""
echo "2. Update the Caddyfile with your domain:"
echo "   nano caddy/Caddyfile"
echo ""
echo "3. Set up SSH key for the 'deploy' user:"
echo "   mkdir -p /home/deploy/.ssh"
echo "   echo 'YOUR_PUBLIC_KEY' >> /home/deploy/.ssh/authorized_keys"
echo "   chown -R deploy:deploy /home/deploy/.ssh"
echo "   chmod 700 /home/deploy/.ssh"
echo "   chmod 600 /home/deploy/.ssh/authorized_keys"
echo ""
echo "4. Configure your domain's DNS to point to this server's IP"
echo ""
echo "5. Start the application:"
echo "   docker compose -f docker-compose.prod.yml up -d"
echo ""
echo -e "${GREEN}🎉 Your server is ready for deployment!${NC}"


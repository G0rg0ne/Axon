# ⚡ Axon

A modern full-stack application with **FastAPI** backend, **Streamlit** frontend, **Docker** containerization, and **Caddy** reverse proxy with automatic HTTPS.

**Live at:** [https://gorgone.app](https://gorgone.app)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         INTERNET                                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CADDY (Reverse Proxy)                        │
│                 Automatic HTTPS / SSL                           │
│          Port 80 (HTTP) → 443 (HTTPS redirect)                  │
└───────────────┬─────────────────────────────────┬───────────────┘
                │                                 │
       gorgone.app                        api.gorgone.app
                │                                 │
                ▼                                 ▼
┌───────────────────────────┐   ┌───────────────────────────┐
│      STREAMLIT            │   │        FASTAPI            │
│      Frontend             │   │        Backend            │
│      Port 8501            │   │        Port 8000          │
└───────────────────────────┘   └───────────────────────────┘
                │                             │
                └──────────────┬──────────────┘
                               │
                               ▼
                    ┌───────────────────┐
                    │     Docker        │
                    │     Network       │
                    └───────────────────┘
```

## 📁 Project Structure

```
Axon/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py          # FastAPI application
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app.py               # Streamlit application
│   ├── Dockerfile
│   └── requirements.txt
├── caddy/
│   └── Caddyfile            # Reverse proxy configuration
├── scripts/
│   ├── setup-server.sh      # Initial server setup
│   └── deploy.sh            # Manual deployment script
├── .github/
│   └── workflows/
│       └── deploy.yml       # CI/CD pipeline
├── docker-compose.yml       # Development environment
├── docker-compose.prod.yml  # Production environment
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Axon.git
   cd Axon
   ```

2. **Start the development environment**
   ```bash
   docker compose up --build
   ```

3. **Access the applications**
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 🌐 Production Deployment

### Step 1: Prepare Your Hetzner Server

1. **Create a new server** on [Hetzner Cloud](https://console.hetzner.cloud/)
   - Recommended: CX22 or higher (2 vCPU, 4GB RAM)
   - OS: Ubuntu 22.04 or 24.04

2. **Note your server's IP address** - you'll need it for DNS configuration

3. **SSH into your server**
   ```bash
   ssh root@YOUR_SERVER_IP
   ```

4. **Run the setup script**
   ```bash
   curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/Axon/main/scripts/setup-server.sh | bash
   ```

   Or manually:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Axon.git /opt/axon
   cd /opt/axon
   chmod +x scripts/setup-server.sh
   sudo ./scripts/setup-server.sh
   ```

### Step 2: Configure DNS

Point your domain to your Hetzner server:

| Type | Name | Value |
|------|------|-------|
| A | @ | YOUR_SERVER_IP |
| A | api | YOUR_SERVER_IP |
| A | www | YOUR_SERVER_IP |

> ⏳ DNS propagation can take up to 48 hours, but usually completes within minutes.

### Step 3: Set Up GitHub Secrets

Add these secrets in your GitHub repository (Settings → Secrets → Actions):

| Secret Name | Value |
|-------------|-------|
| `HETZNER_HOST` | Your server's IP address |
| `HETZNER_USER` | `deploy` (or root) |
| `HETZNER_SSH_KEY` | Your private SSH key |

**Generate SSH key for deployment:**
```bash
# On your local machine
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/axon_deploy

# Copy the public key to your server
ssh-copy-id -i ~/.ssh/axon_deploy.pub deploy@YOUR_SERVER_IP

# The private key content goes in HETZNER_SSH_KEY secret
cat ~/.ssh/axon_deploy
```

### Step 5: Deploy

#### Automatic Deployment (Recommended)
Push to the `main` branch - GitHub Actions will automatically deploy:
```bash
git add .
git commit -m "Initial deployment"
git push origin main
```

#### Manual Deployment
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

#### Direct Server Deployment
```bash
ssh deploy@YOUR_SERVER_IP
cd /opt/axon
docker compose -f docker-compose.prod.yml up -d --build
```

## 🔒 SSL/HTTPS

Caddy automatically handles:
- SSL certificate provisioning via Let's Encrypt
- Certificate renewal
- HTTP → HTTPS redirect
- Modern TLS configuration

No additional configuration needed!

## 🛠️ Useful Commands

### Docker Management
```bash
# View running containers
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs -f

# View specific service logs
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f frontend
docker compose -f docker-compose.prod.yml logs -f caddy

# Restart services
docker compose -f docker-compose.prod.yml restart

# Stop all services
docker compose -f docker-compose.prod.yml down

# Rebuild and restart
docker compose -f docker-compose.prod.yml up -d --build
```

### Debugging
```bash
# Check backend health
curl http://localhost:8000/health

# Enter a container
docker exec -it axon-backend /bin/bash
docker exec -it axon-frontend /bin/bash

# Check Caddy logs for SSL issues
docker compose -f docker-compose.prod.yml logs caddy
```

## 📊 Monitoring

Check container status:
```bash
docker stats
```

View application logs:
```bash
# All logs
docker compose -f docker-compose.prod.yml logs -f

# Last 100 lines
docker compose -f docker-compose.prod.yml logs --tail=100
```

## 🔄 Updating

Simply push to the `main` branch. GitHub Actions will:
1. Run tests
2. SSH to your server
3. Pull latest changes
4. Rebuild containers
5. Restart services

## 📍 Your Endpoints

| URL | Service |
|-----|---------|
| `https://gorgone.app` | Streamlit Frontend |
| `https://api.gorgone.app` | FastAPI Backend |
| `https://api.gorgone.app/docs` | API Documentation |

## 📝 Adding New Features

### Backend (FastAPI)
Add new endpoints in `backend/app/main.py` or create new modules:
```python
@app.get("/api/new-endpoint")
async def new_endpoint():
    return {"message": "Hello!"}
```

### Frontend (Streamlit)
Modify `frontend/app.py` to add new pages or features.

### Database (Optional)
To add a database, update `docker-compose.prod.yml`:
```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - axon-network

volumes:
  postgres_data:
```

## 🐛 Troubleshooting

### Container won't start
```bash
docker compose -f docker-compose.prod.yml logs [service-name]
```

### SSL certificate issues
- Ensure DNS is properly configured
- Check Caddy logs: `docker compose -f docker-compose.prod.yml logs caddy`
- Verify ports 80 and 443 are open

### Connection refused
- Check if containers are running: `docker ps`
- Verify firewall rules: `ufw status`

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

Built with ❤️ using FastAPI, Streamlit, Docker, and Caddy

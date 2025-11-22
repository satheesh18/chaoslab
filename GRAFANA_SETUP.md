# 📊 Grafana Setup Guide for ChaosLab

## Quick Setup with Docker

### 1. Start Grafana Container

```bash
docker run -d \
  -p 3000:3000 \
  --name=chaoslab-grafana \
  -e "GF_SECURITY_ADMIN_PASSWORD=admin" \
  -e "GF_USERS_ALLOW_SIGN_UP=false" \
  grafana/grafana:latest
```

**What this does:**
- Runs Grafana on port 3000
- Sets admin password to `admin`
- Disables user sign-up
- Runs in detached mode

### 2. Access Grafana

1. Open browser: http://localhost:3000
2. Login with:
   - Username: `admin`
   - Password: `admin`
3. (Optional) Change password when prompted

### 3. Create API Token

#### For Grafana 9.0+
1. Go to **Administration** → **Service Accounts**
2. Click **Add service account**
3. Name: `chaoslab`
4. Role: `Editor`
5. Click **Add service account**
6. Click **Add service account token**
7. **Copy the token** (you won't see it again!)

#### For Grafana 8.x
1. Go to **Configuration** (⚙️) → **API Keys**
2. Click **Add API key**
3. Name: `chaoslab`
4. Role: `Editor`
5. Click **Add**
6. **Copy the token**

### 4. Update .env File

```bash
# Grafana Configuration
GRAFANA_MCP_URL=http://localhost:3000
GRAFANA_MCP_TOKEN=your_copied_token_here
```

### 5. Verify Connection

Test the connection:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:3000/api/org
```

Should return: `{"id":1,"name":"Main Org."}`

---

## Alternative: Run Without Grafana

If you want to skip Grafana setup for now:

### Option 1: Mock URLs Only
Just leave Grafana config empty in `.env`:
```bash
# GRAFANA_MCP_URL=http://localhost:3000
# GRAFANA_MCP_TOKEN=
```

The app will generate mock dashboard URLs that look real but won't actually work.

### Option 2: Comment Out Dashboard Creation
In [`backend/main.py`](file:///Users/satheesh/e2b_docker/backend/main.py), you can comment out the Grafana section:
```python
# Create Grafana dashboard
# logger.info(f"Creating Grafana dashboard for {experiment_id}")
# grafana_client = GrafanaClient(...)
# dashboard_url = grafana_client.create_dashboard(...)
dashboard_url = None  # Skip Grafana for now
```

---

## Docker Compose Setup (Recommended)

For a more permanent setup, create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  grafana:
    image: grafana/grafana:latest
    container_name: chaoslab-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_AUTH_ANONYMOUS_ENABLED=true
      - GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer
    volumes:
      - grafana-storage:/var/lib/grafana
    restart: unless-stopped

volumes:
  grafana-storage:
```

Start with:
```bash
docker-compose up -d
```

Stop with:
```bash
docker-compose down
```

---

## Troubleshooting

### Port 3000 Already in Use
```bash
# Find what's using port 3000
lsof -i :3000

# Use different port
docker run -d -p 3001:3000 --name=grafana grafana/grafana
# Update .env: GRAFANA_MCP_URL=http://localhost:3001
```

### Can't Access Grafana
```bash
# Check if container is running
docker ps | grep grafana

# Check logs
docker logs chaoslab-grafana

# Restart container
docker restart chaoslab-grafana
```

### API Token Not Working
- Make sure you copied the entire token
- Check token hasn't expired
- Verify role is `Editor` or `Admin`
- Try creating a new token

### Dashboard Not Appearing
- Check backend logs for Grafana API errors
- Verify token has correct permissions
- Test API connection with curl command above

---

## For Hackathon Demo

### Minimal Setup (5 minutes)
1. `docker run -d -p 3000:3000 grafana/grafana`
2. Login at http://localhost:3000
3. Create API token
4. Add to `.env`
5. Restart backend

### Full Setup (10 minutes)
1. Use docker-compose.yml above
2. Create API token
3. Configure datasource (optional)
4. Test dashboard creation

### Skip Grafana (0 minutes)
1. Leave Grafana config commented in `.env`
2. App will show mock URLs
3. Focus demo on E2B + Groq features

---

## What Grafana Shows

When properly configured, Grafana dashboards display:

- **CPU Usage** - Peak CPU during chaos
- **Memory Usage** - Peak memory consumption
- **Error Count** - Number of errors logged
- **Recovery Time** - Time to recover from chaos

Each panel has color-coded thresholds:
- 🟢 Green: Normal (0-60%)
- 🟡 Yellow: Warning (60-80%)
- 🔴 Red: Critical (80%+)

---

## Next Steps

After Grafana is running:
1. Start ChaosLab backend
2. Run an experiment
3. Check if dashboard URL works
4. If not, check backend logs for errors

**For hackathon:** Even without Grafana, the AI analysis and metrics are the main value proposition!

# Deployment Guide

ClassPilot is a Node.js application with no third-party runtime dependencies. `server.js` serves the interface, demo assets, upload endpoints, and server-side model requests.

## Local deployment

### Windows one-click start

Double-click `start-classpilot.bat`. On first launch it creates `.env` from `.env.example` and opens the platform at `http://localhost:5173/`.

Add your own key after `CHATANYWHERE_API_KEY=`, then restart the server. The editor and classroom player remain available without model credentials.

### macOS or Linux

```bash
chmod +x start-classpilot.sh
./start-classpilot.sh
```

### Manual start

```bash
cp .env.example .env
npm start
```

## Environment variables

```text
PORT=5173

CHATANYWHERE_BASE_URL=https://api.chatanywhere.tech/v1
CHATANYWHERE_API_KEY=

CHATANYWHERE_DEEPSEEK_CHAT_MODEL=deepseek-chat
CHATANYWHERE_DEEPSEEK_REASONER_MODEL=deepseek-v3.2-thinking
CHATANYWHERE_OPENAI_MODEL=gpt-5.6-sol
CHATANYWHERE_CLAUDE_MODEL=claude-sonnet-4-6
CHATANYWHERE_KIMI_MODEL=kimi-k2.5
```

The API key is read only by the server. Do not commit `.env`. The model IDs are ordinary configuration values and may be changed to models available to the ChatAnywhere account.

## Render

The repository includes `render.yaml`.

1. In Render, create a Blueprint from the GitHub repository.
2. Add `CHATANYWHERE_API_KEY`. The model IDs in `render.yaml` may be changed if needed.
3. Deploy and open the assigned Render URL.

Render's free filesystem is ephemeral. The bundled demo assets are restored from the repository on deployment, but files uploaded at runtime are not durable on the free plan.

## Ubuntu with PM2

Install Node.js 18+ and PM2, then run:

```bash
cd /var/www/classpilot
cp .env.example .env
nano .env
sudo npm install -g pm2
pm2 start ecosystem.config.cjs
pm2 save
pm2 startup
```

Open `http://your-server-ip:5173/`.

## Nginx reverse proxy

```nginx
server {
    listen 80;
    server_name your-domain.example;

    client_max_body_size 350M;

    location / {
        proxy_pass http://127.0.0.1:5173;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Use your normal certificate provider or Certbot to enable HTTPS.

## Updating a local deployment

```bash
git pull --ff-only
npm run check
npm test
```

Restart the Node.js process after updating.

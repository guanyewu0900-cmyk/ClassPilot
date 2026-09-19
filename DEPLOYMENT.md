# Deployment Guide

ClassPilot is a Node.js application with no third-party runtime dependencies. `server.js` serves the interface, demo assets, upload endpoints, and server-side model requests.

## Local deployment

### Windows one-click start

Double-click `start-classpilot.bat`. On first launch it creates `.env` from `.env.example` and opens the platform at `http://localhost:5173/`.

Add the API key and model ID for each provider you want to use, then restart the server. The editor and classroom player remain available without model credentials.

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

DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_API_KEY=
DEEPSEEK_CHAT_MODEL=deepseek-chat
DEEPSEEK_REASONER_MODEL=deepseek-reasoner

OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=
OPENAI_MODEL=

ANTHROPIC_BASE_URL=https://api.anthropic.com/v1
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=

KIMI_BASE_URL=https://api.moonshot.cn/v1
KIMI_API_KEY=
KIMI_MODEL=
```

API keys are read only by the server. Do not commit `.env`.

## Render

The repository includes `render.yaml`.

1. In Render, create a Blueprint from the GitHub repository.
2. Add the API key and model ID for each provider used by the public demonstration.
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

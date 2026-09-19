# ClassPilot

ClassPilot is an open-source platform for designing lesson flows, presenting classroom materials, and configuring AI assistants for different stages of a lesson. The included Newton's first law project demonstrates how introduction, experiment, and summary agents can use different prompts and response strategies.

## Features

- Visual course editor and classroom player
- Stage-specific AI assistants with separate prompts and knowledge bases
- Support for DeepSeek, ChatGPT/OpenAI, Claude/Anthropic, and Kimi/Moonshot AI
- PPT/PDF, interactive HTML, quiz, and knowledge-base uploads
- Browser-based course project storage
- One-click local startup on Windows
- Local deployment with operator-controlled files, access, and API credentials

## Privacy and classroom use

The public demonstration is intended for evaluation with non-sensitive example materials. Do not upload personal, sensitive, or identifiable student information to a public deployment.

For school use, deploy ClassPilot on a school-managed computer or server. Course projects are stored in the browser, and uploaded files are stored in the local `uploads/` directory. When a cloud model is used, the prompt, question, and relevant knowledge text required for the request are sent to the provider configured by the operator. See [DATA_AND_PRIVACY.md](DATA_AND_PRIVACY.md).

## Requirements

- Node.js 18 or later
- An API key for at least one model provider if AI chat is required

The course editor and classroom player work without an API key. Only AI responses require provider configuration.

## One-click local start on Windows

1. Download or clone this repository.
2. Double-click `start-classpilot.bat`.
3. Open `http://localhost:5173/` if the browser does not open automatically.

On first launch, the script creates `.env` from `.env.example`. Add the API key and model ID for any provider you want to use, then restart the server.

## Command-line start

```bash
cp .env.example .env
npm start
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
npm.cmd start
```

Open:

```text
http://localhost:5173/
```

## Model configuration

API keys remain on the server and are never sent to the browser.

| Interface option | Required variables |
| --- | --- |
| DeepSeek Chat / Reasoner | `DEEPSEEK_API_KEY` |
| ChatGPT / OpenAI | `OPENAI_API_KEY`, `OPENAI_MODEL` |
| Claude / Anthropic | `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` |
| Kimi / Moonshot AI | `KIMI_API_KEY`, `KIMI_MODEL` |

Set only the providers you intend to use. Model IDs are configurable because availability varies by provider account and region.

## Verification

```bash
npm run check
npm test
```

The smoke test starts local mock model endpoints and verifies static files, bootstrap data, and all four provider routes without using real API keys or making paid requests.

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for Render, Ubuntu/PM2, and reverse-proxy instructions.

## Repository structure

- `server.js`: local web server, uploads, parsers, and model-provider routing
- `studio_teaching_strict_demo.html`: application shell
- `studio_teaching_strict.js`: course editor and classroom player
- `uploads/`: public demonstration assets; runtime uploads are ignored by Git
- `scripts/smoke-test.js`: deterministic local integration test
- `render.yaml`: Render deployment template

## Contributing

Bug reports, classroom feedback, documentation improvements, and code contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

The platform source code is released under the [MIT License](LICENSE). Demo teaching assets are included for evaluation and should be replaced with materials that you are authorized to use in your own deployment.

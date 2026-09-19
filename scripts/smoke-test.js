const assert = require("assert");
const http = require("http");
const path = require("path");
const { spawn } = require("child_process");

function listen(server) {
  return new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", () => resolve(server.address().port));
  });
}

function close(server) {
  return new Promise((resolve) => server.close(resolve));
}

async function getUnusedPort() {
  const server = http.createServer();
  const port = await listen(server);
  await close(server);
  return port;
}

async function waitForHealth(baseUrl, child) {
  for (let attempt = 0; attempt < 60; attempt += 1) {
    if (child.exitCode != null) throw new Error(`ClassPilot exited with code ${child.exitCode}`);
    try {
      const response = await fetch(`${baseUrl}/api/health`);
      if (response.ok) return;
    } catch {}
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  throw new Error("ClassPilot did not become ready");
}

async function main() {
  const requests = [];
  const mockProvider = http.createServer(async (req, res) => {
    const chunks = [];
    for await (const chunk of req) chunks.push(chunk);
    const body = JSON.parse(Buffer.concat(chunks).toString("utf8") || "{}");
    requests.push({ url: req.url, headers: req.headers, body });
    res.setHeader("Content-Type", "application/json");
    if (req.url === "/v1/messages") {
      res.end(JSON.stringify({ content: [{ type: "text", text: `anthropic:${body.model}` }], usage: { input_tokens: 1, output_tokens: 1 } }));
      return;
    }
    if (req.url === "/v1/chat/completions") {
      res.end(JSON.stringify({ choices: [{ message: { content: `openai-compatible:${body.model}` } }], usage: { total_tokens: 2 } }));
      return;
    }
    res.statusCode = 404;
    res.end(JSON.stringify({ error: "not found" }));
  });

  const providerPort = await listen(mockProvider);
  const appPort = await getUnusedPort();
  const providerBase = `http://127.0.0.1:${providerPort}/v1`;
  const root = path.resolve(__dirname, "..");
  const child = spawn(process.execPath, ["server.js"], {
    cwd: root,
    env: {
      ...process.env,
      PORT: String(appPort),
      DEEPSEEK_BASE_URL: providerBase,
      DEEPSEEK_API_KEY: "test",
      OPENAI_BASE_URL: providerBase,
      OPENAI_API_KEY: "test",
      OPENAI_MODEL: "openai-test-model",
      ANTHROPIC_BASE_URL: providerBase,
      ANTHROPIC_API_KEY: "test",
      ANTHROPIC_MODEL: "claude-test-model",
      KIMI_BASE_URL: providerBase,
      KIMI_API_KEY: "test",
      KIMI_MODEL: "kimi-test-model",
    },
    stdio: ["ignore", "pipe", "pipe"],
  });

  let stderr = "";
  child.stderr.on("data", (chunk) => { stderr += chunk.toString(); });
  const baseUrl = `http://127.0.0.1:${appPort}`;

  try {
    await waitForHealth(baseUrl, child);

    const home = await fetch(`${baseUrl}/`);
    assert.strictEqual(home.status, 200);
    assert.match(await home.text(), /ClassPilot|Teaching Studio/i);

    const bootstrap = await fetch(`${baseUrl}/api/bootstrap`);
    assert.strictEqual(bootstrap.status, 200);
    const bootstrapJson = await bootstrap.json();
    assert.ok(Array.isArray(bootstrapJson.projects));
    assert.ok(bootstrapJson.projects.length > 0);

    for (const model of ["deepseek-chat", "deepseek-reasoner", "openai", "claude", "kimi"]) {
      const response = await fetch(`${baseUrl}/api/ai/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model, systemPrompt: "Teach carefully.", knowledge: "Sample", question: "Test" }),
      });
      const data = await response.json();
      assert.strictEqual(response.status, 200, `${model}: ${JSON.stringify(data)}`);
      assert.ok(data.answer);
    }

    const unsupported = await fetch(`${baseUrl}/api/ai/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model: "unknown", question: "Test" }),
    });
    assert.strictEqual(unsupported.status, 400);

    assert.strictEqual(requests.filter((item) => item.url === "/v1/chat/completions").length, 4);
    assert.strictEqual(requests.filter((item) => item.url === "/v1/messages").length, 1);
    console.log("Smoke test passed: UI, bootstrap, DeepSeek, OpenAI, Claude, and Kimi routes.");
  } finally {
    child.kill();
    await close(mockProvider);
  }

  if (stderr) process.stderr.write(stderr);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

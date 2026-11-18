#!/usr/bin/env node
/**
 * opencode-bridge — expose le quota gratuit d'OpenCode comme un fournisseur
 * OpenAI-compatible local, pour Reasonix Studio.
 *
 * Principe : le tier gratuit d'OpenCode (opencode.ai/zen, modèles « *-free »)
 * refuse les appels directs à l'API (HTTP 429 « Free models work in OpenCode »).
 * Il n'est accessible que lorsque c'est OpenCode lui-même qui émet la requête.
 * Ce pont ne vole donc aucune clé : il lance le CLI OpenCode installé et
 * retransmet sa réponse au format /v1/chat/completions.
 *
 * Conséquences assumées :
 *   - pas de function calling (les outils de Reasonix ne passent pas) ;
 *   - un processus CLI par requête (~2-6 s de latence) ;
 *   - aucun historique conservé : chaque appel est une session OpenCode neuve ;
 *   - outils OpenCode désactivés (permission « * » : deny) pour rester en chat.
 */

import http from "node:http";
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));

// ---------------------------------------------------------------- config

const PORT = Number(process.env.OPENCODE_BRIDGE_PORT || 31416);
const HOST = process.env.OPENCODE_BRIDGE_HOST || "127.0.0.1";
const TIMEOUT_MS = Number(process.env.OPENCODE_BRIDGE_TIMEOUT_MS || 180000);
const CWD = process.env.OPENCODE_BRIDGE_CWD || path.join(HERE, "work");

function findCli() {
  if (process.env.OPENCODE_CLI && fs.existsSync(process.env.OPENCODE_CLI)) {
    return process.env.OPENCODE_CLI;
  }
  const base = path.join(
    process.env.APPDATA || path.join(os.homedir(), "AppData", "Roaming"),
    "ai.opencode.desktop",
    "cli"
  );
  if (!fs.existsSync(base)) return null;
  const versions = fs
    .readdirSync(base)
    .filter((d) => fs.existsSync(path.join(base, d, "opencode-cli.exe")))
    .sort((a, b) => b.localeCompare(a, undefined, { numeric: true }));
  return versions.length ? path.join(base, versions[0], "opencode-cli.exe") : null;
}

const CLI = findCli();

// Outils OpenCode coupés : on ne veut que du texte, Reasonix garde la main
// sur les outils. Sans clé ni compte : le tier gratuit reste le seul appelé.
const CHILD_ENV = {
  ...process.env,
  OPENCODE_CONFIG_CONTENT: JSON.stringify({ permission: { "*": "deny" } }),
  OPENCODE_DISABLE_AUTOUPDATE: "1",
};

// ---------------------------------------------------------------- modèles

let modelCache = { at: 0, list: [] };

function freeModels() {
  if (!CLI) return [];
  if (Date.now() - modelCache.at < 10 * 60 * 1000 && modelCache.list.length) {
    return modelCache.list;
  }
  return new Promise((resolve) => {
    const p = spawn(CLI, ["models"], {
      env: CHILD_ENV,
      cwd: fs.mkdtempSync(path.join(os.tmpdir(), "ocb-")),
      stdio: ["ignore", "pipe", "pipe"],
      windowsHide: true,
    });
    let out = "";
    p.stdout.on("data", (d) => (out += d));
    p.on("close", () => {
      // « opencode/<id> » ; on retire le préfixe fournisseur.
      const list = out
        .split(/\r?\n/)
        .map((l) => l.trim())
        .filter((l) => l.startsWith("opencode/") && !l.includes("#"))
        .map((l) => l.slice("opencode/".length));
      modelCache = { at: Date.now(), list };
      resolve(list);
    });
    p.on("error", () => resolve([]));
  });
}

// ---------------------------------------------------------------- exécution

const ANSI = /\x1b\[[0-9;?]*[A-Za-z]|\x1b\][^\x07\x1b]*(\x07|\x1b\\)/g;
const strip = (s) => s.replace(ANSI, "").replace(/\r/g, "");

let queue = Promise.resolve();
function serialize(fn) {
  const run = queue.then(fn, fn);
  queue = run.catch(() => {});
  return run;
}

function transcript(messages) {
  const parts = [];
  for (const m of messages || []) {
    const text =
      typeof m.content === "string"
        ? m.content
        : Array.isArray(m.content)
          ? m.content.map((c) => (typeof c === "string" ? c : c?.text || "")).join("")
          : "";
    if (!text.trim()) continue;
    const role = m.role === "assistant" ? "assistant" : m.role === "system" ? "système" : "user";
    parts.push(`[${role}]\n${text.trim()}`);
  }
  return parts.join("\n\n");
}

function runCli(model, prompt) {
  return new Promise((resolve) => {
    const args = ["run", "--model", `opencode/${model}`, "--", prompt];
    let out = "";
    let err = "";
    let done = false;
    const p = spawn(CLI, args, {
      env: CHILD_ENV,
      cwd: CWD,
      stdio: ["ignore", "pipe", "pipe"],
      windowsHide: true,
    });
    const timer = setTimeout(() => {
      if (!done) {
        done = true;
        try {
          p.kill();
        } catch {}
        resolve({ ok: false, status: 504, text: `délai dépassé (${TIMEOUT_MS} ms)` });
      }
    }, TIMEOUT_MS);
    p.stdout.on("data", (d) => (out += d));
    p.stderr.on("data", (d) => (err += d));
    p.on("error", (e) => {
      if (done) return;
      done = true;
      clearTimeout(timer);
      resolve({ ok: false, status: 502, text: String(e.message || e) });
    });
    p.on("close", (code) => {
      if (done) return;
      done = true;
      clearTimeout(timer);
      const text = strip(out).trim();
      const errText = strip(err).trim();
      if (code === 0 && text) return resolve({ ok: true, status: 200, text });
      const joined = `${errText}\n${text}`;
      const quota = /free usage limit|FreeUsageLimit|subscribe to OpenCode Go/i.test(joined);
      resolve({
        ok: false,
        status: quota ? 429 : 502,
        code: quota ? "free_usage_limit" : "opencode_cli_error",
        text: errText || text || `opencode-cli a quitté avec le code ${code}`,
      });
    });
  });
}

// ---------------------------------------------------------------- HTTP

function json(res, status, body) {
  const payload = JSON.stringify(body);
  res.writeHead(status, {
    "content-type": "application/json; charset=utf-8",
    "content-length": Buffer.byteLength(payload),
    "cache-control": "no-store",
  });
  res.end(payload);
}

function oaiError(res, status, message, code) {
  json(res, status, { error: { message, type: "opencode_bridge_error", code: code || "bridge_error" } });
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let raw = "";
    req.on("data", (d) => {
      raw += d;
      if (raw.length > 32 * 1024 * 1024) reject(new Error("requête trop volumineuse"));
    });
    req.on("end", () => {
      try {
        resolve(raw ? JSON.parse(raw) : {});
      } catch (e) {
        reject(new Error("JSON invalide: " + e.message));
      }
    });
    req.on("error", reject);
  });
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host || "localhost"}`);

  if (req.method === "GET" && (url.pathname === "/health" || url.pathname === "/")) {
    const models = await freeModels();
    return json(res, 200, { ok: Boolean(CLI), cli: CLI, cwd: CWD, models });
  }

  if (req.method === "GET" && url.pathname === "/v1/models") {
    const models = await freeModels();
    return json(res, 200, {
      object: "list",
      data: models.map((id) => ({ id, object: "model", created: 0, owned_by: "opencode" })),
    });
  }

  if (req.method === "POST" && url.pathname === "/v1/chat/completions") {
    if (!CLI) return oaiError(res, 503, "opencode-cli introuvable (OPENCODE_CLI ?)", "cli_missing");

    let body;
    try {
      body = await readBody(req);
    } catch (e) {
      return oaiError(res, 400, e.message, "bad_request");
    }

    const requested = String(body.model || "").replace(/^opencode\//, "");
    const available = await freeModels();
    const model = available.includes(requested) ? requested : available[0];
    if (!model) return oaiError(res, 503, "aucun modèle gratuit listé par opencode", "no_models");

    const prompt = transcript(body.messages);
    if (!prompt) return oaiError(res, 400, "aucun message exploitable", "empty_prompt");

    const result = await serialize(() => runCli(model, prompt));
    if (!result.ok) return oaiError(res, result.status, result.text, result.code);

    const created = Math.floor(Date.now() / 1000);
    const id = `chatcmpl-ocb-${created}-${Math.random().toString(36).slice(2, 8)}`;
    const usage = {
      prompt_tokens: Math.ceil(prompt.length / 4),
      completion_tokens: Math.ceil(result.text.length / 4),
      total_tokens: 0,
    };
    usage.total_tokens = usage.prompt_tokens + usage.completion_tokens;

    if (body.stream) {
      res.writeHead(200, {
        "content-type": "text/event-stream; charset=utf-8",
        "cache-control": "no-store",
        connection: "keep-alive",
      });
      const chunk = {
        id,
        object: "chat.completion.chunk",
        created,
        model,
        choices: [{ index: 0, delta: { role: "assistant", content: result.text }, finish_reason: null }],
      };
      res.write(`data: ${JSON.stringify(chunk)}\n\n`);
      res.write(
        `data: ${JSON.stringify({ ...chunk, choices: [{ index: 0, delta: {}, finish_reason: "stop" }] })}\n\n`
      );
      res.write("data: [DONE]\n\n");
      return res.end();
    }

    return json(res, 200, {
      id,
      object: "chat.completion",
      created,
      model,
      choices: [{ index: 0, message: { role: "assistant", content: result.text }, finish_reason: "stop" }],
      usage,
    });
  }

  oaiError(res, 404, `route inconnue: ${req.method} ${url.pathname}`, "not_found");
});

fs.mkdirSync(CWD, { recursive: true });
if (!CLI) {
  console.error("[opencode-bridge] opencode-cli.exe introuvable — définis OPENCODE_CLI.");
}
server.listen(PORT, HOST, () => {
  console.log(`[opencode-bridge] http://${HOST}:${PORT}/v1  (cli: ${CLI || "absent"})`);
  console.log(`[opencode-bridge] cwd des sessions: ${CWD}`);
});

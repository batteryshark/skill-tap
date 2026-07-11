#!/usr/bin/env node
// Single-file, zero-dependency OCR utility.
// Sends images to an OpenAI-compatible local endpoint (LM Studio, vLLM, etc.)
// using Node's built-in fetch. Requires Node 18+.

import { readFile, readdir, mkdir, writeFile, stat } from "node:fs/promises";
import path from "node:path";
import process from "node:process";

const DEFAULT_BASE_URL = "http://127.0.0.1:1234/v1";
const DEFAULT_PROMPT =
  "OCR this document to fully capture the text. If the text is source code like python, properly format the code.";
const DEFAULT_API_KEY = "lm-studio";

const THINKING_DISABLE_CANDIDATES = [
  ["chat_template_kwargs.enable_thinking", { chat_template_kwargs: { enable_thinking: false } }],
  ["enable_thinking", { enable_thinking: false }],
  ["thinking.enabled", { thinking: { enabled: false } }],
  ["reasoning_effort=low", { reasoning_effort: "low" }],
];

const IMAGE_EXTENSIONS = new Set([
  ".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff", ".heic", ".heif",
]);

const MIME_BY_EXT = {
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp",
  ".gif": "image/gif",
  ".bmp": "image/bmp",
  ".tif": "image/tiff",
  ".tiff": "image/tiff",
  ".heic": "image/heic",
  ".heif": "image/heif",
};

const USAGE = `Run OCR on image(s) using a locally hosted OpenAI-compatible vision model endpoint.

Usage: local-ocr-vlm [images...] [options]

Positional:
  images                    Optional path(s) to image file(s) to OCR.

Options:
  --input-dir <dir>         Directory of images to OCR (processes all images in the folder).
  --base-url <url>          OpenAI-compatible base URL (default: ${DEFAULT_BASE_URL})
  --api-key <key>           API key for compatibility (default: ${DEFAULT_API_KEY})
  --model <id>              Model ID. If omitted, uses the first model returned by /models.
  --prompt <text>          Prompt text (default: "${DEFAULT_PROMPT}")
  --output-dir <dir>        Output directory for markdown files. If omitted, prints to stdout.
  --max-workers <n>         Parallel OCR requests (default: 4). Set to 1 for sequential.
  --enable-thinking         Allow model reasoning/thinking mode (default: try to disable it).
  --preflight-timeout <s>   Timeout (seconds) for preflight checks and probing (default: 10).
  -h, --help                Show this help.
`;

function parseArgs(argv) {
  const args = {
    images: [],
    inputDir: null,
    baseUrl: DEFAULT_BASE_URL,
    apiKey: DEFAULT_API_KEY,
    model: null,
    prompt: DEFAULT_PROMPT,
    outputDir: null,
    maxWorkers: 4,
    enableThinking: false,
    preflightTimeout: 10.0,
  };

  const needsValue = (name) => {
    throw new Error(`Option ${name} requires a value`);
  };

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    const next = () => (i + 1 < argv.length ? argv[++i] : needsValue(arg));
    switch (arg) {
      case "-h":
      case "--help":
        process.stdout.write(USAGE);
        process.exit(0);
        break;
      case "--input-dir": args.inputDir = next(); break;
      case "--base-url": args.baseUrl = next(); break;
      case "--api-key": args.apiKey = next(); break;
      case "--model": args.model = next(); break;
      case "--prompt": args.prompt = next(); break;
      case "--output-dir": args.outputDir = next(); break;
      case "--max-workers": args.maxWorkers = parseInt(next(), 10); break;
      case "--enable-thinking": args.enableThinking = true; break;
      case "--preflight-timeout": args.preflightTimeout = parseFloat(next()); break;
      default:
        if (arg.startsWith("-") && arg !== "-") {
          throw new Error(`Unknown option: ${arg}`);
        }
        args.images.push(arg);
    }
  }
  return args;
}

function guessMime(filePath) {
  return MIME_BY_EXT[path.extname(filePath).toLowerCase()] || "application/octet-stream";
}

async function encodeImageAsDataUrl(filePath) {
  const buf = await readFile(filePath);
  return `data:${guessMime(filePath)};base64,${buf.toString("base64")}`;
}

async function isImageFile(filePath) {
  try {
    const s = await stat(filePath);
    if (!s.isFile()) return false;
  } catch {
    return false;
  }
  return IMAGE_EXTENSIONS.has(path.extname(filePath).toLowerCase());
}

async function collectImages(images, inputDir) {
  const resolved = [];
  const seen = new Set();

  for (const image of images) {
    const key = path.resolve(image);
    if (seen.has(key)) continue;
    resolved.push(image);
    seen.add(key);
  }

  if (inputDir != null) {
    let entries;
    try {
      entries = await readdir(inputDir);
    } catch (err) {
      if (err.code === "ENOENT") throw new Error(`Input directory not found: ${inputDir}`);
      if (err.code === "ENOTDIR") throw new Error(`Not a directory: ${inputDir}`);
      throw err;
    }
    entries.sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase()));
    for (const name of entries) {
      const full = path.join(inputDir, name);
      const key = path.resolve(full);
      if ((await isImageFile(full)) && !seen.has(key)) {
        resolved.push(full);
        seen.add(key);
      }
    }
  }

  if (resolved.length === 0) {
    throw new Error(
      "No input images found. Provide image paths and/or --input-dir with image files."
    );
  }
  return resolved;
}

function isQwen35(modelId) {
  const m = modelId.toLowerCase();
  return ["3.5", "3_5", "3-5", "qwen3"].some((t) => m.includes(t));
}

function is9b(modelId) {
  const m = modelId.toLowerCase();
  return ["9b", "9-b", "9 b"].some((t) => m.includes(t));
}

function is27b(modelId) {
  const m = modelId.toLowerCase();
  return ["27b", "27-b", "27 b"].some((t) => m.includes(t));
}

function selectPreferredModel(modelIds) {
  if (modelIds.length === 0) return null;
  const checks = [
    (m) => m.toLowerCase().includes("qwen") && isQwen35(m) && is9b(m),
    (m) => m.toLowerCase().includes("qwen") && is9b(m),
    (m) => m.toLowerCase().includes("qwen") && isQwen35(m) && is27b(m),
    (m) => m.toLowerCase().includes("qwen") && is27b(m),
  ];
  for (const check of checks) {
    const found = modelIds.find(check);
    if (found) return found;
  }
  return null;
}

function resolveModel(modelIds, model) {
  if (model) return model;
  if (modelIds.length === 0) {
    throw new Error(
      "No models returned by the endpoint. Load a model in LM Studio, vLLM/vmlx, or pass --model explicitly."
    );
  }
  const preferred = selectPreferredModel(modelIds);
  if (preferred) {
    console.log(`[info] Auto-selected preferred model: ${preferred}`);
    return preferred;
  }
  return modelIds[0];
}

// --- REST helpers -----------------------------------------------------------

function joinUrl(baseUrl, endpoint) {
  return `${baseUrl.replace(/\/+$/, "")}/${endpoint.replace(/^\/+/, "")}`;
}

async function apiPost(baseUrl, apiKey, endpoint, body, timeoutMs) {
  const controller = timeoutMs ? new AbortController() : null;
  const timer = controller ? setTimeout(() => controller.abort(), timeoutMs) : null;
  try {
    const res = await fetch(joinUrl(baseUrl, endpoint), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify(body),
      signal: controller ? controller.signal : undefined,
    });
    const text = await res.text();
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${text.slice(0, 500)}`);
    }
    return text ? JSON.parse(text) : {};
  } finally {
    if (timer) clearTimeout(timer);
  }
}

async function fetchAvailableModels(baseUrl, apiKey, timeoutMs) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(joinUrl(baseUrl, "models"), {
      headers: { Authorization: `Bearer ${apiKey}` },
      signal: controller.signal,
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    return (json.data || []).map((m) => m.id);
  } catch (err) {
    throw new Error(
      `Could not reach ${baseUrl}. Start LM Studio or another OpenAI-compatible ` +
        `endpoint (such as vLLM/vmlx) and make sure the /v1 API is available. (${err.message})`
    );
  } finally {
    clearTimeout(timer);
  }
}

function isThinkingParamError(err) {
  const text = String(err.message || err).toLowerCase();
  const thinkingHints = ["enable_thinking", "chat_template_kwargs", "reasoning_effort", "thinking", "extra_body"];
  const unsupportedHints = ["unknown", "unexpected", "unsupported", "invalid", "extra fields", "not permitted", "not allowed"];
  return thinkingHints.some((h) => text.includes(h)) && unsupportedHints.some((h) => text.includes(h));
}

async function pickThinkingDisablePayload(baseUrl, apiKey, model, enableThinking, timeoutMs) {
  if (enableThinking) return [null, null];

  for (const [label, extra] of THINKING_DISABLE_CANDIDATES) {
    try {
      await apiPost(
        baseUrl,
        apiKey,
        "chat/completions",
        {
          model,
          temperature: 0,
          max_tokens: 4,
          messages: [{ role: "user", content: "Reply with OK." }],
          ...extra,
        },
        timeoutMs
      );
      return [extra, label];
    } catch (err) {
      if (isThinkingParamError(err)) continue;
      console.error(`[warn] Thinking-disable probe failed for '${label}': ${err.message}`);
      return [null, null];
    }
  }
  return [null, null];
}

async function ocrImage(baseUrl, apiKey, model, imagePath, prompt, thinkingExtra) {
  if (!(await isImageFile(imagePath))) {
    // Distinguish missing vs non-file for a clearer error, matching the original.
    try {
      const s = await stat(imagePath);
      if (!s.isFile()) throw new Error(`Not a file: ${imagePath}`);
    } catch {
      throw new Error(`File not found: ${imagePath}`);
    }
  }

  const dataUrl = await encodeImageAsDataUrl(imagePath);
  const body = {
    model,
    temperature: 0,
    messages: [
      {
        role: "user",
        content: [
          { type: "text", text: prompt },
          { type: "image_url", image_url: { url: dataUrl } },
        ],
      },
    ],
    ...(thinkingExtra || {}),
  };

  const completion = await apiPost(baseUrl, apiKey, "chat/completions", body, null);
  const text = completion?.choices?.[0]?.message?.content;
  return text ? text.trim() : "";
}

async function writeMarkdown(outputDir, imagePath, text) {
  await mkdir(outputDir, { recursive: true });
  const stem = path.basename(imagePath, path.extname(imagePath));
  const outPath = path.join(outputDir, `${stem}.md`);
  const content = `# OCR Output: ${path.basename(imagePath)}\n\n${text}\n`;
  await writeFile(outPath, content, "utf-8");
  return outPath;
}

async function emitResult(outputDir, imagePath, text) {
  if (outputDir) {
    const outPath = await writeMarkdown(outputDir, imagePath, text);
    console.log(`[ok] ${imagePath} -> ${outPath}`);
    return;
  }
  console.log(`===== ${imagePath} =====`);
  console.log(text);
  console.log();
}

async function runPool(items, maxWorkers, worker) {
  let index = 0;
  const runNext = async () => {
    while (index < items.length) {
      const i = index++;
      await worker(items[i]);
    }
  };
  const workers = [];
  for (let w = 0; w < Math.min(maxWorkers, items.length); w++) {
    workers.push(runNext());
  }
  await Promise.all(workers);
}

async function main() {
  let args;
  try {
    args = parseArgs(process.argv.slice(2));
  } catch (err) {
    console.error(err.message);
    return 1;
  }

  if (!Number.isFinite(args.maxWorkers) || args.maxWorkers < 1) {
    console.error("--max-workers must be >= 1");
    return 1;
  }
  if (!Number.isFinite(args.preflightTimeout) || args.preflightTimeout <= 0) {
    console.error("--preflight-timeout must be > 0");
    return 1;
  }

  let images;
  try {
    images = await collectImages(args.images, args.inputDir);
  } catch (err) {
    console.error(`Failed to resolve input images: ${err.message}`);
    return 1;
  }

  const preflightTimeoutMs = args.preflightTimeout * 1000;

  let modelIds;
  try {
    modelIds = await fetchAvailableModels(args.baseUrl, args.apiKey, preflightTimeoutMs);
  } catch (err) {
    console.error(`Failed to reach endpoint: ${err.message}`);
    return 1;
  }

  let model;
  try {
    model = resolveModel(modelIds, args.model);
  } catch (err) {
    console.error(`Failed to resolve model: ${err.message}`);
    return 1;
  }

  const [thinkingExtra, thinkingLabel] = await pickThinkingDisablePayload(
    args.baseUrl, args.apiKey, model, args.enableThinking, preflightTimeoutMs
  );
  if (!args.enableThinking) {
    if (thinkingLabel) {
      console.log(`[info] Thinking mode disabled via: ${thinkingLabel}`);
    } else {
      console.error(
        "[warn] Could not apply known thinking-disable parameters. Continuing with endpoint defaults."
      );
    }
  }

  let anyFailures = false;
  const workers = args.maxWorkers;

  await runPool(images, workers, async (image) => {
    try {
      const text = await ocrImage(args.baseUrl, args.apiKey, model, image, args.prompt, thinkingExtra);
      await emitResult(args.outputDir, image, text);
    } catch (err) {
      anyFailures = true;
      console.error(`[error] ${image}: ${err.message}`);
    }
  });

  return anyFailures ? 1 : 0;
}

main().then((code) => process.exit(code));

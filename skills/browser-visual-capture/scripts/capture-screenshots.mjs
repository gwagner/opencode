#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { mkdir } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { basename, join, resolve } from 'node:path';
import { spawn, spawnSync } from 'node:child_process';

const DEFAULT_OUTPUT_DIR = '/tmp/opencode-browser-visual-capture';

function usage() {
  return `Usage: node capture-screenshots.mjs --phase baseline|post-change [options] <url...>

Options:
  --phase <phase>        Required: baseline or post-change.
  --run-id <id>          Run directory id; defaults to timestamp.
  --output-dir <path>    Output parent directory under /tmp. Default: ${DEFAULT_OUTPUT_DIR}
  --urls-file <path>     File with one URL per line; # comments ignored.
  --viewport <WxH>       Viewport size. Default: 1280x720
  --wait-ms <ms>         Fixed wait after page load. Default: 750
  --timeout-ms <ms>      Per-page timeout. Default: 15000
  --chrome <path>        Chromium executable path.
  --help                 Show this help.
`;
}

function parseArgs(argv) {
  const options = {
    outputDir: DEFAULT_OUTPUT_DIR,
    viewport: '1280x720',
    waitMs: 750,
    timeoutMs: 15000,
    urls: [],
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    const next = () => {
      if (i + 1 >= argv.length) throw new Error(`Missing value for ${arg}`);
      i += 1;
      return argv[i];
    };

    if (arg === '--help' || arg === '-h') {
      options.help = true;
    } else if (arg === '--phase') {
      options.phase = next();
    } else if (arg === '--run-id') {
      options.runId = next();
    } else if (arg === '--output-dir') {
      options.outputDir = next();
    } else if (arg === '--urls-file') {
      options.urlsFile = next();
    } else if (arg === '--viewport') {
      options.viewport = next();
    } else if (arg === '--wait-ms') {
      options.waitMs = Number.parseInt(next(), 10);
    } else if (arg === '--timeout-ms') {
      options.timeoutMs = Number.parseInt(next(), 10);
    } else if (arg === '--chrome') {
      options.chrome = next();
    } else if (arg.startsWith('--')) {
      throw new Error(`Unknown option: ${arg}`);
    } else {
      options.urls.push(arg);
    }
  }

  return options;
}

function parseViewport(value) {
  const match = /^(\d+)x(\d+)$/i.exec(value);
  if (!match) throw new Error(`Invalid viewport '${value}'. Expected WIDTHxHEIGHT.`);
  return { width: Number.parseInt(match[1], 10), height: Number.parseInt(match[2], 10) };
}

function readUrls(options) {
  const urls = [...options.urls];
  if (options.urlsFile) {
    const content = readFileSync(resolve(options.urlsFile), 'utf8');
    for (const line of content.split(/\r?\n/)) {
      const trimmed = line.trim();
      if (trimmed && !trimmed.startsWith('#')) urls.push(trimmed);
    }
  }
  return [...new Set(urls)].map((raw) => {
    const url = new URL(raw);
    if (!['http:', 'https:'].includes(url.protocol)) {
      throw new Error(`Unsupported URL protocol for '${raw}'. Use http or https.`);
    }
    return url.toString();
  });
}

function safeSegment(value, fallback = 'page') {
  return (value || fallback)
    .toLowerCase()
    .replace(/[^a-z0-9._-]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 64) || fallback;
}

function defaultRunId() {
  return new Date().toISOString().replace(/[:.]/g, '-');
}

function tmpOutputPath(path) {
  const resolved = resolve(path);
  if (resolved !== '/tmp' && !resolved.startsWith('/tmp/')) {
    throw new Error('--output-dir must resolve under /tmp.');
  }
  return resolved;
}

function findChrome(explicit) {
  if (explicit) {
    if (!existsSync(explicit)) throw new Error(`Chromium executable not found: ${explicit}`);
    return explicit;
  }
  for (const command of ['chromium', 'chromium-browser', 'google-chrome', 'google-chrome-stable']) {
    const result = spawnSync('sh', ['-lc', `command -v ${command}`], { encoding: 'utf8' });
    const found = result.stdout.trim();
    if (result.status === 0 && found) return found;
  }
  throw new Error('No Chromium executable found. Install chromium or pass --chrome <path>.');
}

function wait(ms) {
  return new Promise((resolveWait) => setTimeout(resolveWait, ms));
}

async function waitForFile(path, timeoutMs) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    if (existsSync(path)) return;
    await wait(50);
  }
  throw new Error(`Timed out waiting for ${basename(path)}`);
}

class CdpClient {
  constructor(socket) {
    this.socket = socket;
    this.nextId = 1;
    this.pending = new Map();
    this.listeners = new Map();
    socket.addEventListener('message', (event) => this.handleMessage(event.data));
  }

  handleMessage(raw) {
    const message = JSON.parse(raw);
    if (message.id && this.pending.has(message.id)) {
      const { resolveCommand, rejectCommand } = this.pending.get(message.id);
      this.pending.delete(message.id);
      if (message.error) rejectCommand(new Error(message.error.message));
      else resolveCommand(message.result || {});
      return;
    }
    if (message.method && this.listeners.has(message.method)) {
      for (const listener of this.listeners.get(message.method)) listener(message.params || {});
    }
  }

  send(method, params = {}) {
    const id = this.nextId;
    this.nextId += 1;
    const payload = JSON.stringify({ id, method, params });
    return new Promise((resolveCommand, rejectCommand) => {
      this.pending.set(id, { resolveCommand, rejectCommand });
      this.socket.send(payload);
    });
  }

  once(method, timeoutMs) {
    return new Promise((resolveEvent, rejectEvent) => {
      const remove = (listener) => {
        const listeners = this.listeners.get(method) || [];
        this.listeners.set(method, listeners.filter((candidate) => candidate !== listener));
      };
      const timer = setTimeout(() => {
        remove(listener);
        rejectEvent(new Error(`Timed out waiting for ${method}`));
      }, timeoutMs);
      const listener = (params) => {
        clearTimeout(timer);
        remove(listener);
        resolveEvent(params);
      };
      this.listeners.set(method, [...(this.listeners.get(method) || []), listener]);
    });
  }
}

async function launchChrome(chrome) {
  const userDataDir = mkdtempSync(join(tmpdir(), 'opencode-browser-visual-capture-'));
  const child = spawn(chrome, [
    '--headless=new',
    '--no-sandbox',
    '--disable-gpu',
    '--disable-dev-shm-usage',
    '--disable-extensions',
    '--no-first-run',
    '--no-default-browser-check',
    '--remote-debugging-port=0',
    `--user-data-dir=${userDataDir}`,
    'about:blank',
  ], { stdio: ['ignore', 'ignore', 'pipe'] });

  child.stderr.setEncoding('utf8');
  await waitForFile(join(userDataDir, 'DevToolsActivePort'), 10000);
  const [port] = readFileSync(join(userDataDir, 'DevToolsActivePort'), 'utf8').split(/\r?\n/);
  return { child, userDataDir, port };
}

async function stopChrome(browser) {
  if (!browser.child.killed) browser.child.kill('SIGTERM');
  await Promise.race([
    new Promise((resolveStop) => browser.child.once('exit', resolveStop)),
    wait(2000).then(() => {
      if (!browser.child.killed) browser.child.kill('SIGKILL');
    }),
  ]);
  rmSync(browser.userDataDir, { recursive: true, force: true });
}

async function connectPage(port) {
  const tabs = await fetch(`http://127.0.0.1:${port}/json`).then((response) => response.json());
  const page = tabs.find((tab) => tab.type === 'page') || tabs[0];
  if (!page?.webSocketDebuggerUrl) throw new Error('Could not locate Chromium DevTools page target.');
  const socket = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((resolveSocket, rejectSocket) => {
    socket.addEventListener('open', resolveSocket, { once: true });
    socket.addEventListener('error', rejectSocket, { once: true });
  });
  return new CdpClient(socket);
}

async function captureUrl(client, url, options, viewport, outputDir, index) {
  const parsed = new URL(url);
  const slug = safeSegment(`${parsed.hostname}${parsed.pathname === '/' ? '' : parsed.pathname}`);
  const hash = createHash('sha256').update(url).digest('hex').slice(0, 12);
  const filename = `${safeSegment(options.phase)}-${String(index + 1).padStart(3, '0')}-${hash}-${slug}-${viewport.width}x${viewport.height}.png`;
  const path = join(outputDir, filename);

  const loaded = client.once('Page.loadEventFired', options.timeoutMs);
  const navigation = await client.send('Page.navigate', { url });
  if (navigation.errorText) {
    loaded.catch(() => {});
    throw new Error(`Navigation failed: ${navigation.errorText}`);
  }
  await loaded;
  await wait(options.waitMs);
  const result = await client.send('Page.captureScreenshot', { format: 'png', fromSurface: true });
  writeFileSync(path, Buffer.from(result.data, 'base64'));
  return path;
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  if (options.help) {
    process.stdout.write(usage());
    return 0;
  }
  if (!['baseline', 'post-change'].includes(options.phase)) {
    throw new Error('--phase must be baseline or post-change.');
  }
  if (!Number.isFinite(options.waitMs) || options.waitMs < 0) throw new Error('--wait-ms must be >= 0.');
  if (!Number.isFinite(options.timeoutMs) || options.timeoutMs <= 0) throw new Error('--timeout-ms must be > 0.');

  const viewport = parseViewport(options.viewport);
  const urls = readUrls(options);
  if (urls.length === 0) throw new Error('Provide at least one URL or --urls-file.');

  const chrome = findChrome(options.chrome);
  const runId = safeSegment(options.runId || defaultRunId(), 'run');
  const runDir = resolve(tmpOutputPath(options.outputDir), runId);
  await mkdir(runDir, { recursive: true });

  const summary = {
    phase: options.phase,
    runId,
    outputDir: runDir,
    viewport,
    waitMs: options.waitMs,
    timeoutMs: options.timeoutMs,
    chrome,
    startedAt: new Date().toISOString(),
    results: [],
  };

  const browser = await launchChrome(chrome);
  try {
    const client = await connectPage(browser.port);
    await client.send('Page.enable');
    await client.send('Network.enable');
    await client.send('Emulation.setDeviceMetricsOverride', {
      width: viewport.width,
      height: viewport.height,
      deviceScaleFactor: 1,
      mobile: false,
    });
    await client.send('Emulation.setEmulatedMedia', {
      media: 'screen',
      features: [
        { name: 'prefers-reduced-motion', value: 'reduce' },
        { name: 'prefers-color-scheme', value: 'light' },
      ],
    });

    for (const [index, url] of urls.entries()) {
      try {
        const screenshotPath = await captureUrl(client, url, options, viewport, runDir, index);
        summary.results.push({ url, ok: true, screenshotPath });
        process.stdout.write(`saved ${screenshotPath}\n`);
      } catch (error) {
        summary.results.push({ url, ok: false, error: error.message });
        process.stderr.write(`failed ${url}: ${error.message}\n`);
      }
    }
  } finally {
    await stopChrome(browser);
  }

  summary.finishedAt = new Date().toISOString();
  const summaryPath = join(runDir, `${safeSegment(options.phase)}-summary.json`);
  writeFileSync(summaryPath, `${JSON.stringify(summary, null, 2)}\n`);
  process.stdout.write(`summary ${summaryPath}\n`);
  return summary.results.every((result) => result.ok) ? 0 : 1;
}

main()
  .then((code) => process.exit(code))
  .catch((error) => {
    process.stderr.write(`${error.message}\n${usage()}`);
    process.exit(1);
  });

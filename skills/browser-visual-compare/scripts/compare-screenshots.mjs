#!/usr/bin/env node

import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { inflateSync } from 'node:zlib';

function usage() {
  return `Usage: node compare-screenshots.mjs --manifest <path> --baseline-summary <path> --post-change-summary <path> [--output <path>]\n`;
}

function parseArgs(argv) {
  const options = {};
  const names = new Map([
    ['--manifest', 'manifest'],
    ['--baseline-summary', 'baselineSummary'],
    ['--post-change-summary', 'postChangeSummary'],
    ['--output', 'output'],
  ]);
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === '--help' || arg === '-h') return { help: true };
    const name = names.get(arg);
    if (!name) throw new Error(`Unknown option: ${arg}`);
    if (index + 1 >= argv.length) throw new Error(`Missing value for ${arg}`);
    options[name] = argv[index + 1];
    index += 1;
  }
  for (const name of ['manifest', 'baselineSummary', 'postChangeSummary']) {
    if (!options[name]) throw new Error(`Missing required option --${name.replace(/[A-Z]/g, (letter) => `-${letter.toLowerCase()}`)}`);
  }
  return options;
}

function tmpPath(path) {
  const absolute = resolve(path);
  if (absolute !== '/tmp' && !absolute.startsWith('/tmp/')) {
    throw new Error('--output must resolve under /tmp.');
  }
  return absolute;
}

function readJson(path, label) {
  try {
    return JSON.parse(readFileSync(resolve(path), 'utf8'));
  } catch (error) {
    throw new Error(`Could not read ${label} '${path}': ${error.message}`);
  }
}

function assertString(value, label) {
  if (typeof value !== 'string' || value.trim() === '') throw new Error(`${label} must be a nonempty string.`);
}

function validateRegion(region, label, width, height) {
  if (!region || typeof region !== 'object' || Array.isArray(region)) throw new Error(`${label} must be an object.`);
  for (const key of ['x', 'y', 'width', 'height']) {
    if (!Number.isInteger(region[key])) throw new Error(`${label}.${key} must be an integer.`);
  }
  if (region.x < 0 || region.y < 0 || region.width <= 0 || region.height <= 0) {
    throw new Error(`${label} must have nonnegative coordinates and positive dimensions.`);
  }
  if (region.x + region.width > width || region.y + region.height > height) {
    throw new Error(`${label} exceeds the ${width}x${height} screenshot.`);
  }
}

function parsePng(path) {
  const input = readFileSync(path);
  const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
  if (input.length < 8 || !input.subarray(0, 8).equals(signature)) throw new Error(`Not a PNG: ${path}`);

  let offset = 8;
  let header;
  const compressed = [];
  while (offset + 12 <= input.length) {
    const length = input.readUInt32BE(offset);
    const type = input.toString('ascii', offset + 4, offset + 8);
    const start = offset + 8;
    const end = start + length;
    if (end + 4 > input.length) throw new Error(`Truncated PNG chunk in ${path}`);
    if (type === 'IHDR') {
      header = {
        width: input.readUInt32BE(start),
        height: input.readUInt32BE(start + 4),
        bitDepth: input[start + 8],
        colorType: input[start + 9],
        interlace: input[start + 12],
      };
    } else if (type === 'IDAT') compressed.push(input.subarray(start, end));
    else if (type === 'IEND') break;
    offset = end + 4;
  }
  if (!header || compressed.length === 0) throw new Error(`PNG lacks IHDR or IDAT data: ${path}`);
  const channels = new Map([[0, 1], [2, 3], [4, 2], [6, 4]]).get(header.colorType);
  if (header.bitDepth !== 8 || !channels || header.interlace !== 0) {
    throw new Error(`Unsupported PNG encoding in ${path}; require noninterlaced 8-bit grayscale, RGB, grayscale-alpha, or RGBA.`);
  }

  const stride = header.width * channels;
  const raw = inflateSync(Buffer.concat(compressed));
  if (raw.length !== (stride + 1) * header.height) throw new Error(`Unexpected PNG data length in ${path}`);
  const decoded = Buffer.alloc(stride * header.height);
  for (let y = 0; y < header.height; y += 1) {
    const filter = raw[y * (stride + 1)];
    if (filter > 4) throw new Error(`Unsupported PNG filter ${filter} in ${path}`);
    const source = y * (stride + 1) + 1;
    const target = y * stride;
    for (let x = 0; x < stride; x += 1) {
      const value = raw[source + x];
      const left = x >= channels ? decoded[target + x - channels] : 0;
      const up = y > 0 ? decoded[target - stride + x] : 0;
      const upperLeft = y > 0 && x >= channels ? decoded[target - stride + x - channels] : 0;
      let predictor = 0;
      if (filter === 1) predictor = left;
      else if (filter === 2) predictor = up;
      else if (filter === 3) predictor = Math.floor((left + up) / 2);
      else if (filter === 4) {
        const p = left + up - upperLeft;
        const pa = Math.abs(p - left);
        const pb = Math.abs(p - up);
        const pc = Math.abs(p - upperLeft);
        predictor = pa <= pb && pa <= pc ? left : (pb <= pc ? up : upperLeft);
      }
      decoded[target + x] = (value + predictor) & 255;
    }
  }

  const rgba = Buffer.alloc(header.width * header.height * 4);
  for (let pixel = 0; pixel < header.width * header.height; pixel += 1) {
    const source = pixel * channels;
    const target = pixel * 4;
    if (header.colorType === 0 || header.colorType === 4) {
      rgba[target] = decoded[source];
      rgba[target + 1] = decoded[source];
      rgba[target + 2] = decoded[source];
      rgba[target + 3] = header.colorType === 4 ? decoded[source + 1] : 255;
    } else {
      rgba[target] = decoded[source];
      rgba[target + 1] = decoded[source + 1];
      rgba[target + 2] = decoded[source + 2];
      rgba[target + 3] = header.colorType === 6 ? decoded[source + 3] : 255;
    }
  }
  return { width: header.width, height: header.height, rgba };
}

function contains(region, x, y) {
  return x >= region.x && x < region.x + region.width && y >= region.y && y < region.y + region.height;
}

function summaryRoutes(summary, expectedPhase, label) {
  if (summary.phase !== expectedPhase || !Array.isArray(summary.results)) {
    throw new Error(`${label} must be a ${expectedPhase} capture summary with results.`);
  }
  const routes = new Map();
  for (const result of summary.results) {
    assertString(result.url, `${label} result URL`);
    if (routes.has(result.url)) throw new Error(`${label} contains duplicate route '${result.url}'.`);
    routes.set(result.url, result);
  }
  return routes;
}

function compareEntry(entry, index, baselineRoutes, postChangeRoutes) {
  const label = `comparisons[${index}]`;
  for (const key of ['id', 'route', 'state', 'rationale', 'acceptanceOutcome']) assertString(entry?.[key], `${label}.${key}`);
  if (!['unchanged', 'changed'].includes(entry.expected)) throw new Error(`${label}.expected must be unchanged or changed.`);
  if (typeof entry.allowedDiffThreshold !== 'number' || !Number.isFinite(entry.allowedDiffThreshold)
      || entry.allowedDiffThreshold < 0 || entry.allowedDiffThreshold > 1) {
    throw new Error(`${label}.allowedDiffThreshold must be a number from 0 through 1.`);
  }
  for (const key of ['expectedChangedRegions', 'ignoredRegions']) {
    if (entry[key] !== undefined && !Array.isArray(entry[key])) throw new Error(`${label}.${key} must be an array.`);
  }
  if (entry.expected === 'unchanged' && (entry.expectedChangedRegions?.length || 0) > 0) {
    throw new Error(`${label}.expectedChangedRegions is valid only when expected is changed.`);
  }

  const baselineResult = baselineRoutes.get(entry.route);
  const postChangeResult = postChangeRoutes.get(entry.route);
  if (!baselineResult || !postChangeResult) throw new Error(`${label}.route is missing from one or both capture summaries.`);
  if (!baselineResult.ok || !postChangeResult.ok) throw new Error(`${label}.route has a failed capture.`);
  for (const result of [baselineResult, postChangeResult]) {
    assertString(result.screenshotPath, `${label} screenshotPath`);
    if (!existsSync(result.screenshotPath)) throw new Error(`Screenshot does not exist: ${result.screenshotPath}`);
  }

  const baseline = parsePng(baselineResult.screenshotPath);
  const postChange = parsePng(postChangeResult.screenshotPath);
  if (baseline.width !== postChange.width || baseline.height !== postChange.height) {
    throw new Error(`${label} screenshot dimensions differ.`);
  }
  const expectedRegions = entry.expectedChangedRegions || [];
  const ignoredRegions = entry.ignoredRegions || [];
  expectedRegions.forEach((region, regionIndex) => validateRegion(region, `${label}.expectedChangedRegions[${regionIndex}]`, baseline.width, baseline.height));
  ignoredRegions.forEach((region, regionIndex) => validateRegion(region, `${label}.ignoredRegions[${regionIndex}]`, baseline.width, baseline.height));

  let comparedPixels = 0;
  let changedPixels = 0;
  let changedOutsideExpectedRegions = 0;
  const changedByExpectedRegion = expectedRegions.map(() => 0);
  for (let y = 0; y < baseline.height; y += 1) {
    for (let x = 0; x < baseline.width; x += 1) {
      if (ignoredRegions.some((region) => contains(region, x, y))) continue;
      comparedPixels += 1;
      const offset = (y * baseline.width + x) * 4;
      if (baseline.rgba.subarray(offset, offset + 4).equals(postChange.rgba.subarray(offset, offset + 4))) continue;
      changedPixels += 1;
      if (expectedRegions.length > 0) {
        let inExpectedRegion = false;
        expectedRegions.forEach((region, regionIndex) => {
          if (contains(region, x, y)) {
            changedByExpectedRegion[regionIndex] += 1;
            inExpectedRegion = true;
          }
        });
        if (!inExpectedRegion) changedOutsideExpectedRegions += 1;
      }
    }
  }
  if (comparedPixels === 0) throw new Error(`${label} ignores every screenshot pixel.`);
  const diffRatio = changedPixels / comparedPixels;
  const reasons = [];
  if (diffRatio > entry.allowedDiffThreshold) reasons.push(`diff ratio ${diffRatio} exceeds allowed threshold ${entry.allowedDiffThreshold}`);
  if (entry.expected === 'changed' && changedPixels === 0) reasons.push('expected a change but no nonignored pixels changed');
  if (expectedRegions.length > 0 && changedOutsideExpectedRegions > 0) reasons.push(`${changedOutsideExpectedRegions} changed pixels are outside expected regions`);
  changedByExpectedRegion.forEach((count, regionIndex) => {
    if (count === 0) reasons.push(`expected changed region ${regionIndex} contains no changed nonignored pixels`);
  });

  return {
    id: entry.id,
    route: entry.route,
    state: entry.state,
    expected: entry.expected,
    status: reasons.length === 0 ? 'pass' : 'fail',
    rationale: entry.rationale,
    acceptanceOutcome: entry.acceptanceOutcome,
    metrics: {
      width: baseline.width,
      height: baseline.height,
      comparedPixels,
      changedPixels,
      diffRatio,
      allowedDiffThreshold: entry.allowedDiffThreshold,
      changedOutsideExpectedRegions,
      changedByExpectedRegion,
    },
    reasons,
  };
}

function writeReport(path, report) {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, `${JSON.stringify(report, null, 2)}\n`);
  process.stdout.write(`comparison ${path}\n`);
}

function main() {
  let options;
  try {
    options = parseArgs(process.argv.slice(2));
    if (options.help) {
      process.stdout.write(usage());
      return 0;
    }
  } catch (error) {
    process.stderr.write(`${error.message}\n${usage()}`);
    return 1;
  }

  let outputPath;
  try {
    outputPath = tmpPath(options.output || resolve(dirname(options.postChangeSummary), 'comparison.json'));
    const manifest = readJson(options.manifest, 'manifest');
    const baselineSummary = readJson(options.baselineSummary, 'baseline summary');
    const postChangeSummary = readJson(options.postChangeSummary, 'post-change summary');
    if (manifest.version !== 1 || !Array.isArray(manifest.comparisons) || manifest.comparisons.length === 0) {
      throw new Error('Manifest must have version 1 and a nonempty comparisons array.');
    }
    const ids = new Set();
    for (const [index, entry] of manifest.comparisons.entries()) {
      assertString(entry?.id, `comparisons[${index}].id`);
      if (ids.has(entry.id)) throw new Error(`Duplicate comparison id '${entry.id}'.`);
      ids.add(entry.id);
    }
    const baselineRoutes = summaryRoutes(baselineSummary, 'baseline', 'baseline summary');
    const postChangeRoutes = summaryRoutes(postChangeSummary, 'post-change', 'post-change summary');
    const comparisons = manifest.comparisons.map((entry, index) => {
      try {
        return compareEntry(entry, index, baselineRoutes, postChangeRoutes);
      } catch (error) {
        return { id: entry.id, route: entry.route, state: entry.state, status: 'error', reasons: [error.message] };
      }
    });
    const outcome = comparisons.some((entry) => entry.status === 'error')
      ? 'execution_error'
      : (comparisons.some((entry) => entry.status === 'fail') ? 'failed_expectation' : 'success');
    writeReport(outputPath, {
      version: 1,
      outcome,
      manifest: resolve(options.manifest),
      baselineSummary: resolve(options.baselineSummary),
      postChangeSummary: resolve(options.postChangeSummary),
      comparisons,
    });
    return outcome === 'success' ? 0 : (outcome === 'failed_expectation' ? 2 : 1);
  } catch (error) {
    const report = { version: 1, outcome: 'execution_error', error: error.message, comparisons: [] };
    if (outputPath) {
      try { writeReport(outputPath, report); } catch (writeError) { process.stderr.write(`Could not write comparison report: ${writeError.message}\n`); }
    }
    process.stderr.write(`${error.message}\n`);
    return 1;
  }
}

process.exit(main());

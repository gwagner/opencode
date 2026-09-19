import assert from 'node:assert/strict';
import { mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import test from 'node:test';
import { deflateSync } from 'node:zlib';

const script = new URL('../scripts/compare-screenshots.mjs', import.meta.url).pathname;

function crc32(buffer) {
  let crc = 0xffffffff;
  for (const byte of buffer) {
    crc ^= byte;
    for (let bit = 0; bit < 8; bit += 1) crc = (crc >>> 1) ^ ((crc & 1) ? 0xedb88320 : 0);
  }
  return (crc ^ 0xffffffff) >>> 0;
}

function chunk(type, data) {
  const name = Buffer.from(type);
  const output = Buffer.alloc(data.length + 12);
  output.writeUInt32BE(data.length, 0);
  name.copy(output, 4);
  data.copy(output, 8);
  output.writeUInt32BE(crc32(Buffer.concat([name, data])), data.length + 8);
  return output;
}

function png(width, height, pixels) {
  const header = Buffer.alloc(13);
  header.writeUInt32BE(width, 0);
  header.writeUInt32BE(height, 4);
  header[8] = 8;
  header[9] = 6;
  const rows = [];
  for (let y = 0; y < height; y += 1) rows.push(Buffer.concat([Buffer.from([0]), pixels.subarray(y * width * 4, (y + 1) * width * 4)]));
  return Buffer.concat([
    Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]),
    chunk('IHDR', header),
    chunk('IDAT', deflateSync(Buffer.concat(rows))),
    chunk('IEND', Buffer.alloc(0)),
  ]);
}

function runCase(expected, baselinePixels, postPixels, extra = {}) {
  const directory = mkdtempSync(join(tmpdir(), 'visual-compare-test-'));
  const route = 'https://example.test/page';
  const baselinePath = join(directory, 'baseline.png');
  const postPath = join(directory, 'post.png');
  writeFileSync(baselinePath, png(2, 1, Buffer.from(baselinePixels)));
  writeFileSync(postPath, png(2, 1, Buffer.from(postPixels)));
  const baselineSummary = join(directory, 'baseline-summary.json');
  const postSummary = join(directory, 'post-change-summary.json');
  writeFileSync(baselineSummary, JSON.stringify({ phase: 'baseline', results: [{ url: route, ok: true, screenshotPath: baselinePath }] }));
  writeFileSync(postSummary, JSON.stringify({ phase: 'post-change', results: [{ url: route, ok: true, screenshotPath: postPath }] }));
  const manifest = join(directory, 'manifest.json');
  writeFileSync(manifest, JSON.stringify({
    version: 1,
    comparisons: [{
      id: 'page-default', route, state: 'default', expected, allowedDiffThreshold: 0.5,
      rationale: 'fixture', acceptanceOutcome: 'fixture accepted', ...extra,
    }],
  }));
  const output = join(directory, 'comparison.json');
  const result = spawnSync(process.execPath, [script, '--manifest', manifest, '--baseline-summary', baselineSummary, '--post-change-summary', postSummary, '--output', output], { encoding: 'utf8' });
  return { result, report: JSON.parse(readFileSync(output, 'utf8')) };
}

const black = [0, 0, 0, 255, 0, 0, 0, 255];
const oneWhite = [255, 255, 255, 255, 0, 0, 0, 255];

test('passes unchanged and bounded changed expectations', () => {
  const unchanged = runCase('unchanged', black, black);
  assert.equal(unchanged.result.status, 0);
  assert.equal(unchanged.report.outcome, 'success');

  const changed = runCase('changed', black, oneWhite, { expectedChangedRegions: [{ x: 0, y: 0, width: 1, height: 1 }] });
  assert.equal(changed.result.status, 0);
  assert.equal(changed.report.comparisons[0].metrics.changedPixels, 1);
});

test('failed expectations exit 2 and remain distinct from execution errors', () => {
  const failed = runCase('unchanged', black, oneWhite, { allowedDiffThreshold: 0 });
  assert.equal(failed.result.status, 2);
  assert.equal(failed.report.outcome, 'failed_expectation');

  const errored = runCase('changed', black, oneWhite, { expectedChangedRegions: [{ x: 2, y: 0, width: 1, height: 1 }] });
  assert.equal(errored.result.status, 1);
  assert.equal(errored.report.outcome, 'execution_error');
  assert.equal(errored.report.comparisons[0].status, 'error');
});

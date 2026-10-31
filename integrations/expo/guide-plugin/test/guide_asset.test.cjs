'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { installGuide, validateGuide } = require('../guide_asset.cjs');

const FIXTURE = path.resolve(__dirname,
  '../../../../sample/src/main/assets/aya-guide.md');
const PACKAGE = 'dev.aya.sample';
const VERSION = '1.0.0';

function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'aya-expo-guide-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const android = path.join(root, 'android');
  const sourcePath = path.join(root, 'support', 'aya-guide.md');
  fs.mkdirSync(path.dirname(sourcePath), { recursive: true });
  fs.mkdirSync(android);
  fs.copyFileSync(FIXTURE, sourcePath);
  return {
    root, android, sourcePath,
    output: path.join(android, 'app/src/main/assets/aya-guide.md'),
    marker: path.join(android, 'app/.aya-guide-prebuild.json'),
    args: {
      projectRoot: root,
      platformProjectRoot: android,
      guidePath: 'support/aya-guide.md',
      packageName: PACKAGE,
      versionName: VERSION,
    },
  };
}

test('installs exact native asset, retains content, and is idempotent', t => {
  const f = fixture(t);
  const result = installGuide(f.args);
  assert.equal(result.packageName, PACKAGE);
  assert.deepEqual(fs.readFileSync(f.output), fs.readFileSync(f.sourcePath));
  assert.equal(installGuide(f.args).sha256, result.sha256);
  assert.equal(JSON.parse(fs.readFileSync(f.marker, 'utf8')).format,
    'aya-expo-guide/v1');
});

test('updates only its own unchanged prior guide', t => {
  const f = fixture(t);
  installGuide(f.args);
  fs.appendFileSync(f.sourcePath, '\nCI host fixture updated with new source evidence.\n');
  installGuide(f.args);
  assert.deepEqual(fs.readFileSync(f.output), fs.readFileSync(f.sourcePath));
});

test('rejects tampered previously owned native guide', t => {
  const f = fixture(t);
  installGuide(f.args);
  fs.writeFileSync(f.output, 'manually modified foreign content');
  assert.throws(() => installGuide(f.args), /modified or unrelated/);
  assert.equal(fs.readFileSync(f.output, 'utf8'), 'manually modified foreign content');
});

test('rejects unrelated preexisting native guide', t => {
  const f = fixture(t);
  fs.mkdirSync(path.dirname(f.output), { recursive: true });
  fs.writeFileSync(f.output, 'foreign source');
  assert.throws(() => installGuide(f.args), /unowned existing native/);
  assert.equal(fs.readFileSync(f.output, 'utf8'), 'foreign source');
});

test('rejects unrelated or corrupted provenance metadata', t => {
  const f = fixture(t);
  installGuide(f.args);
  fs.writeFileSync(f.marker, JSON.stringify({ format: 'other', sourcePath: 'other' }));
  assert.throws(() => installGuide(f.args), /unrelated prebuild provenance/);
});

test('rejects traversal, absolute paths and Windows separators', t => {
  const f = fixture(t);
  for (const guidePath of ['../outside.md', '/tmp/outside.md',
                           'support/../aya-guide.md',
                           'support\\aya-guide.md', 'support//aya-guide.md']) {
    assert.throws(() => installGuide({ ...f.args, guidePath }), /safe relative/);
  }
});

test('rejects symlinked source or native destination', t => {
  const f = fixture(t);
  const real = f.sourcePath;
  const external = path.join(f.root, 'external.md');
  fs.copyFileSync(real, external);
  fs.unlinkSync(real);
  fs.symlinkSync(external, real);
  assert.throws(() => installGuide(f.args), /symbolic links/);
});

test('rejects a symlinked native asset directory without writing outside', t => {
  const f = fixture(t);
  const dir = path.dirname(f.output);
  const outside = path.join(f.root, 'external-assets');
  fs.mkdirSync(path.dirname(dir), { recursive: true });
  fs.mkdirSync(outside);
  fs.symlinkSync(outside, dir);
  assert.throws(() => installGuide(f.args), /symbolic links/);
  assert.equal(fs.existsSync(path.join(outside, 'aya-guide.md')), false);
});

test('rejects a different app identity or installed version', t => {
  const f = fixture(t);
  assert.throws(() => installGuide({ ...f.args, packageName: 'org.other' }),
    /app_id does not match/);
  assert.throws(() => installGuide({ ...f.args, versionName: '2.0.0' }),
    /guide version does not match/);
  assert.equal(fs.existsSync(f.output), false);
});

test('rejects malformed, missing sections and invalid Unicode', t => {
  const f = fixture(t);
  const content = fs.readFileSync(f.sourcePath);
  const truncated = Buffer.from(content.toString('utf8').replace(
    '## Assistant answer policy', '## Unrecognized section'));
  assert.throws(() => validateGuide(truncated, PACKAGE, VERSION),
    /missing or duplicate AYA-RAS section/);
  assert.throws(() => validateGuide(Buffer.from([0xc3, 0x28]), PACKAGE, VERSION),
    /invalid UTF-8/);
  assert.throws(() => validateGuide(Buffer.alloc(2 * 1024 * 1024 + 1),
    PACKAGE, VERSION), /no larger than/);
});

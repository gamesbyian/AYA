'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const withAyaGuide = require('../app.plugin.js');

test('a locally linked guide plugin resolves the Expo config API from its host project', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'aya-expo-host-resolution-'));
  const cwd = process.cwd();
  try {
    const expo = path.join(root, 'node_modules', 'expo');
    fs.mkdirSync(expo, { recursive: true });
    fs.writeFileSync(path.join(root, 'package.json'), '{"private":true}');
    fs.writeFileSync(path.join(expo, 'config-plugins.js'),
      'module.exports = { withDangerousMod: (config, mod) => ({ ...config, ayaMod: mod }) };');
    process.chdir(root);
    const result = withAyaGuide(
      { android: { package: 'dev.aya.cihost' }, version: '1.0.0' },
      { guidePath: 'aya-guide.md' }
    );
    assert.equal(result.ayaMod[0], 'android');
    assert.equal(typeof result.ayaMod[1], 'function');
  } finally {
    process.chdir(cwd);
    fs.rmSync(root, { recursive: true, force: true });
  }
});

test('missing Expo host dependency fails instead of silently installing a different API', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'aya-expo-absent-host-'));
  const cwd = process.cwd();
  try {
    fs.writeFileSync(path.join(root, 'package.json'), '{"private":true}');
    process.chdir(root);
    assert.throws(() => withAyaGuide(
      { android: { package: 'dev.aya.cihost' }, version: '1.0.0' },
      { guidePath: 'aya-guide.md' }
    ), /Cannot find module 'expo\/config-plugins'/);
  } finally {
    process.chdir(cwd);
    fs.rmSync(root, { recursive: true, force: true });
  }
});

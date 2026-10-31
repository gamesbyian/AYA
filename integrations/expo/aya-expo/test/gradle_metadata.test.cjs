'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

test('the Expo Android library declares publication versionName from its own package version', () => {
  const source = fs.readFileSync(
    path.join(__dirname, '../android/build.gradle'), 'utf8'
  );
  assert.match(source, /apply plugin: 'expo-module-gradle-plugin'/);
  assert.match(source, /version\s*=\s*'0\.1\.0-dev\.1'/);
  assert.match(source, /versionName\s+project\.version\.toString\(\)/);
  assert.doesNotMatch(source, /versionName\s+['"]1\.0\.0['"]/);
});

'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');

const NATIVE_SOURCE = fs.readFileSync(
  path.join(__dirname, '../src/native.ts'), 'utf8'
);

function loadNative({ platform = 'android', response = {status: 'review_opened'}, missing = false } = {}) {
  const calls = [];
  const output = ts.transpileModule(NATIVE_SOURCE, {
    compilerOptions: {
      module: ts.ModuleKind.CommonJS,
      target: ts.ScriptTarget.ES2022,
    },
  }).outputText;
  const exported = {};
  const native = missing ? null : {
    openHelp: async (...args) => {
      calls.push(args);
      if (response instanceof Error) throw response;
      return response;
    },
  };
  const context = {
    exports: exported,
    require: module => {
      if (module === 'react-native') return { Platform: { OS: platform } };
      if (module === 'expo-modules-core') {
        return {requireOptionalNativeModule: (name) => {
          assert.equal(name, 'AyaExpo');
          return native;
        }};
      }
      throw new Error('Unexpected module ' + module);
    },
  };
  vm.runInNewContext(output, context, {timeout: 1000});
  return {openAyaHelp: exported.openAyaHelp, calls};
}

test('guarded native open means local review only, not recipient success', async () => {
  const { openAyaHelp, calls } = loadNative();
  const result = await openAyaHelp({
    question: 'How do I open an app?', screenName: 'Support',
    askQuestion: false,
  });
  assert.equal(result.status, 'review_opened');
  assert.deepEqual(calls, [['aya-guide.md', 'Support',
    'How do I open an app?', false]]);
});

test('bare headless help opens AYA question composer by default', async () => {
  const {openAyaHelp, calls} = loadNative({response: {status: 'question_opened'}});
  const result = await openAyaHelp();
  assert.equal(result.status, 'question_opened');
  assert.deepEqual(calls, [['aya-guide.md', null, '', true]]);
});

test('a host-supplied question uses local review without a duplicate composer', async () => {
  const {openAyaHelp, calls} = loadNative();
  assert.equal((await openAyaHelp({question: 'How do I use it?'})).status, 'review_opened');
  assert.deepEqual(calls, [['aya-guide.md', null, 'How do I use it?', false]]);
});

test('an explicit composer override is respected even with a host field', async () => {
  const {openAyaHelp, calls} = loadNative({response: {status: 'question_opened'}});
  assert.equal((await openAyaHelp({question: '', askQuestion: true})).status, 'question_opened');
  assert.deepEqual(calls, [['aya-guide.md', null, '', true]]);
});

test('missing native module cannot fake success or use unguarded sharing', async () => {
  const {openAyaHelp, calls} = loadNative({missing: true});
  assert.equal((await openAyaHelp()).status, 'rejected');
  assert.equal(calls.length, 0);
});

test('web and iOS are deliberately unsupported', async () => {
  for (const platform of ['ios', 'web']) {
    const {openAyaHelp, calls} = loadNative({platform});
    assert.equal((await openAyaHelp()).status, 'rejected');
    assert.equal(calls.length, 0);
  }
});

test('unsafe guide path and invalid typed input reject without dispatch', async () => {
  for (const options of [
    {guideAsset: '../aya-guide.md'},
    {guideAsset: '/tmp/aya-guide.md'},
    {guideAsset: 'https://example.com/guide.md'},
    {guideAsset: 'a\\b.md'},
    {guideAsset: 'docs//guide.md'},
    {guideAsset: 'docs/./guide.md'},
    {question: 123}, {screenName: 123}, {askQuestion: 'false'},
  ]) {
    const {openAyaHelp, calls} = loadNative();
    assert.equal((await openAyaHelp(options)).status, 'rejected');
    assert.equal(calls.length, 0);
  }
});

test('unrecognized statuses reject rather than implying AI completion', async () => {
  for (const response of [
    {status: 'agent_finished'}, {status: 'share_completed'},
    null, 'review_opened', {}, {status: null},
  ]) {
    const {openAyaHelp} = loadNative({response});
    assert.equal((await openAyaHelp()).status, 'rejected');
  }
});

test('native errors are local rejections', async () => {
  const {openAyaHelp} = loadNative({response: new Error('native activity detached')});
  assert.equal((await openAyaHelp({question: 'Open help'})).status, 'rejected');
});

test('native rejection message is retained without inventing results', async () => {
  const {openAyaHelp} = loadNative({
    response: {status: 'rejected', reason: 'Missing exact-version AYA guide.'},
  });
  const result = await openAyaHelp();
  assert.equal(result.status, 'rejected');
  assert.match(result.reason, /exact-version/);
});

test('Kotlin bridge routes through guarded AyaComponentAction.Help', () => {
  const kt = fs.readFileSync(path.join(__dirname,
    '../android/src/main/java/dev/aya/expo/AyaExpoModule.kt'), 'utf8');
  assert.match(kt, /AyaComponentAction\.Help\(/);
  assert.match(kt, /\.launch\(host, text = question\)/);
  assert.match(kt, /host\.runOnUiThread/);
  assert.doesNotMatch(kt, /ACTION_SEND|startActivity\(|onAgentAnswered/);
});

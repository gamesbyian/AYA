'use strict';

const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const { TextDecoder } = require('node:util');

const REQUIRED_SECTIONS = Object.freeze([
  'Scope and version',
  'Quick orientation',
  'Navigation map',
  'Task recipes',
  'Features and settings',
  'Troubleshooting',
  'Limitations and unsupported behavior',
  'Privacy and data handling',
  'Glossary and synonyms',
  'Evidence and provenance',
  'Unknowns and escalation',
  'Assistant answer policy',
]);

const METADATA = Object.freeze([
  'schema_version', 'app_id', 'app_name', 'app_version_min',
  'app_version_max', 'platform', 'locale', 'guide_revision',
  'source_revision', 'last_verified_utc', 'owner',
]);

function fail(message) {
  throw new Error('AYA Expo guide prebuild: ' + message);
}

function sha256(bytes) {
  return crypto.createHash('sha256').update(bytes).digest('hex');
}

function validateGuide(bytes, packageName, versionName) {
  if (!Buffer.isBuffer(bytes) || bytes.length === 0 || bytes.length > 2 * 1024 * 1024) {
    fail('guide must be a nonempty UTF-8 file no larger than 2 MiB');
  }
  let content;
  try {
    content = new TextDecoder('utf-8', { fatal: true }).decode(bytes);
  } catch (_) {
    fail('guide contains invalid UTF-8');
  }
  if (content.charCodeAt(0) === 0xfeff) fail('remove the UTF-8 BOM');
  const lines = content.split(/\r?\n/);
  if (lines[0] !== '---') fail('AYA-RAS metadata delimiter is missing');
  const end = lines.indexOf('---', 1);
  if (end <= 1) fail('AYA-RAS metadata is incomplete');
  const meta = Object.create(null);
  for (const line of lines.slice(1, end)) {
    if (!line.trim()) continue;
    const match = /^([a-z][a-z0-9_]*):\s*(.*?)\s*$/.exec(line);
    if (!match) fail('invalid reference metadata entry');
    const key = match[1];
    if (Object.hasOwn(meta, key)) fail('duplicate reference metadata: ' + key);
    meta[key] = match[2].replace(/^["']|["']$/g, '').trim();
  }
  for (const key of METADATA) {
    if (!meta[key]) fail('missing reference metadata: ' + key);
  }
  if (meta.schema_version !== 'aya-reference/v1' || meta.platform !== 'android') {
    fail('unsupported AYA reference schema/platform');
  }
  if (typeof packageName !== 'string' || !packageName ||
      meta.app_id !== packageName) {
    fail('guide app_id does not match the configured Expo Android package');
  }
  if (typeof versionName !== 'string' || !versionName ||
      meta.app_version_min !== versionName || meta.app_version_max !== versionName) {
    fail('guide version does not match Expo version; use an exact-version guide');
  }
  const body = lines.slice(end + 1).join('\n');
  if (!body.trim()) fail('reference body is empty');
  const headings = Array.from(body.matchAll(/^## (.+?)\s*$/gm), match => match[1].trim());
  for (const section of REQUIRED_SECTIONS) {
    if (headings.filter(value => value === section).length !== 1) {
      fail('missing or duplicate AYA-RAS section: ' + section);
    }
  }
  if (/<[A-Za-z][^>\n]{2,80}>/.test(content)) {
    fail('guide contains unresolved authoring placeholders');
  }
  return meta;
}

function assertRelativeGuidePath(relative) {
  if (typeof relative !== 'string' || !relative ||
      path.isAbsolute(relative) || relative.includes('\\') ||
      relative.split('/').some(s => !s || s === '.' || s === '..') ||
      !relative.endsWith('.md')) {
    fail('guidePath must be a safe relative Markdown file inside the Expo project');
  }
}

function containedIn(root, child) {
  const relative = path.relative(root, child);
  return relative === '' || (relative !== '..' && !relative.startsWith('..' + path.sep) &&
    !path.isAbsolute(relative));
}

function rejectSymlinks(root, destination) {
  if (!containedIn(root, destination)) fail('path escaped the project root');
  const relative = path.relative(root, destination);
  let current = root;
  for (const segment of relative.split(path.sep)) {
    if (!segment) continue;
    current = path.join(current, segment);
    try {
      if (fs.lstatSync(current).isSymbolicLink()) {
        fail('symbolic links are forbidden for guide inputs and native output paths');
      }
    } catch (error) {
      if (error.code !== 'ENOENT') throw error;
    }
  }
}

function atomicWrite(file, bytes) {
  const temporary = file + '.aya-' + process.pid + '-' + crypto.randomBytes(6).toString('hex');
  try {
    fs.writeFileSync(temporary, bytes, { flag: 'wx', mode: 0o644 });
    fs.renameSync(temporary, file);
  } finally {
    try { fs.unlinkSync(temporary); } catch (error) {
      if (error.code !== 'ENOENT') throw error;
    }
  }
}

/**
 * Copy a host-authored guide into native Android assets. Never create app
 * documentation, never overwrite a foreign/modified existing native guide.
 * A plugin-owned prior guide may be updated only when its recorded hash
 * still proves the destination was not modified independently.
 */
function installGuide({
  projectRoot, platformProjectRoot, guidePath, packageName, versionName,
}) {
  assertRelativeGuidePath(guidePath);
  const project = fs.realpathSync(projectRoot);
  const android = fs.realpathSync(platformProjectRoot);
  if (!containedIn(project, android)) fail('Android native project lies outside the Expo project');
  const source = path.resolve(project, guidePath);
  rejectSymlinks(project, source);
  if (!fs.statSync(source).isFile()) fail('guide source must be a regular file');
  const bytes = fs.readFileSync(source);
  validateGuide(bytes, packageName, versionName);

  const app = path.join(android, 'app');
  const assetDir = path.join(app, 'src', 'main', 'assets');
  const destination = path.join(assetDir, 'aya-guide.md');
  const provenance = path.join(app, '.aya-guide-prebuild.json');
  rejectSymlinks(android, destination);
  rejectSymlinks(android, provenance);
  const expectedHash = sha256(bytes);

  if (fs.existsSync(destination)) {
    const previous = fs.readFileSync(destination);
    if (!fs.statSync(destination).isFile()) fail('guide destination must be a regular file');
    if (!previous.equals(bytes)) {
      let recorded;
      try {
        recorded = JSON.parse(fs.readFileSync(provenance, 'utf8'));
      } catch (_) {
        fail('refusing to replace an unowned existing native aya-guide.md');
      }
      if (!recorded || recorded.sourcePath !== guidePath ||
          recorded.sha256 !== sha256(previous)) {
        fail('refusing to overwrite a modified or unrelated native aya-guide.md');
      }
    }
  }

  fs.mkdirSync(assetDir, { recursive: true });
  if (!fs.existsSync(destination) || !fs.readFileSync(destination).equals(bytes)) {
    atomicWrite(destination, bytes);
  }
  const record = Buffer.from(JSON.stringify({
    format: 'aya-expo-guide/v1',
    sourcePath: guidePath,
    sha256: expectedHash,
    packageName,
    versionName,
  }, null, 2) + '\n', 'utf8');
  if (fs.existsSync(provenance) &&
      !fs.statSync(provenance).isFile()) fail('provenance must be a regular file');
  atomicWrite(provenance, record);
  return { destination, packageName, versionName, sha256: expectedHash };
}

module.exports = {
  installGuide, validateGuide, assertRelativeGuidePath, REQUIRED_SECTIONS,
};

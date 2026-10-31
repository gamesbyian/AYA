'use strict';

/**
 * Expo CNG / prebuild hook. Android native module integration remains
 * separate: this only installs the correct guide, never enables a backend.
 */
module.exports = function withAyaGuide(config, options = {}) {
  // A local file: dependency may resolve this plugin from its source directory
  // outside the host's node_modules. Bind dependency resolution to the Expo
  // application, so this code uses that host's own config-plugin API rather
  // than requiring a second copy of Expo next to the plugin source.
  const { createRequire } = require('node:module');
  const path = require('node:path');
  const hostRequire = createRequire(path.join(process.cwd(), 'package.json'));
  const { withDangerousMod } = hostRequire('expo/config-plugins');
  const { installGuide } = require('./guide_asset.cjs');
  if (!options || typeof options.guidePath !== 'string') {
    throw new Error('AYA Expo: provide { guidePath: "path/to/verified-guide.md" }');
  }
  if (!config.android || !config.android.package || !config.version) {
    throw new Error('AYA Expo: configure explicit android.package and version');
  }
  return withDangerousMod(config, ['android', async next => {
    installGuide({
      projectRoot: next.modRequest.projectRoot,
      platformProjectRoot: next.modRequest.platformProjectRoot,
      guidePath: options.guidePath,
      packageName: next.android.package,
      versionName: next.version,
    });
    return next;
  }]);
};

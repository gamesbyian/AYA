'use strict';

/**
 * Expo CNG / prebuild hook. Android native module integration remains
 * separate: this only installs the correct guide, never enables a backend.
 */
module.exports = function withAyaGuide(config, options = {}) {
  const { withDangerousMod } = require('expo/config-plugins');
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

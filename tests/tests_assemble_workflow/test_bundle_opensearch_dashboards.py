# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

import os
import unittest
from unittest.mock import MagicMock, call, patch

from assemble_workflow.bundle_opensearch_dashboards import \
    BundleOpenSearchDashboards
from manifests.build_manifest import BuildManifest
from paths.script_finder import ScriptFinder


class TestBundleOpenSearchDashboards(unittest.TestCase):
    def test_bundle_opensearch_dashboards(self):
        manifest_path = os.path.join(
            os.path.dirname(__file__), "data/opensearch-dashboards-build-1.1.0.yml"
        )
        artifacts_path = os.path.join(os.path.dirname(__file__), "data/artifacts")
        bundle = BundleOpenSearchDashboards(
            BuildManifest.from_path(manifest_path), artifacts_path, MagicMock()
        )
        self.assertEqual(bundle.min_tarball.name, "OpenSearch-Dashboards")
        self.assertEqual(len(bundle.plugins), 1)
        self.assertEqual(bundle.artifacts_dir, artifacts_path)
        self.assertIsNotNone(bundle.bundle_recorder)
        self.assertEqual(bundle.installed_plugins, [])
        self.assertTrue(
            bundle.min_tarball_path.endswith(
                "/opensearch-dashboards-min-1.1.0-linux-x64.tar.gz"
            )
        )
        self.assertIsNotNone(bundle.archive_path)

    @patch("os.path.isfile", return_value=True)
    def test_bundle_install_plugin(self, *mocks):
        manifest_path = os.path.join(
            os.path.dirname(__file__), "data/opensearch-dashboards-build-1.1.0.yml"
        )
        artifacts_path = os.path.join(os.path.dirname(__file__), "data/artifacts")
        bundle = BundleOpenSearchDashboards(
            BuildManifest.from_path(manifest_path), artifacts_path, MagicMock()
        )

        plugin = bundle.plugins[0]  # alertingDashboards

        with patch("shutil.copyfile") as mock_copyfile:
            with patch("subprocess.check_call") as mock_check_call:
                bundle.install_plugin(plugin)

                self.assertEqual(mock_copyfile.call_count, 1)
                self.assertEqual(mock_check_call.call_count, 2)

                install_plugin_bin = os.path.join(
                    bundle.archive_path, "bin/opensearch-dashboards-plugin"
                )
                mock_check_call.assert_has_calls(
                    [
                        call(
                            f'{install_plugin_bin} --allow-root install file:{os.path.join(bundle.tmp_dir.name, "alertingDashboards-1.1.0.zip")}',
                            cwd=bundle.archive_path,
                            shell=True,
                        ),
                        call(
                            f'{ScriptFinder.find_install_script("alertingDashboards-1.1.0.zip")} -a "{artifacts_path}" -o "{bundle.archive_path}"',
                            cwd=bundle.archive_path,
                            shell=True,
                        ),
                    ]
                )

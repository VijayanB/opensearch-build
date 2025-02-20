# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

import os
import unittest
from unittest.mock import MagicMock, call, patch

from manifests_workflow.input_manifests_opensearch_dashboards import \
    InputManifestsOpenSearchDashboards


class TestInputManifestsOpenSearchDashboards(unittest.TestCase):
    def test_files(self):
        files = InputManifestsOpenSearchDashboards.files()
        self.assertTrue(len(files) >= 1)
        manifest = os.path.realpath(
            os.path.join(
                os.path.dirname(__file__),
                "../../manifests/1.1.0/opensearch-dashboards-1.1.0.yml",
            )
        )
        self.assertTrue(manifest in files)

    @patch("os.makedirs")
    @patch("os.chdir")
    @patch(
        "manifests_workflow.input_manifests.InputManifest.from_path"
    )
    @patch(
        "manifests_workflow.input_manifests_opensearch_dashboards.ComponentOpenSearchDashboardsMin"
    )
    @patch("system.temporary_directory.TemporaryDirectory")
    @patch("manifests_workflow.input_manifests.InputManifest")
    def test_update(
        self,
        mock_input_manifest,
        mock_tmpdir,
        mock_component_opensearch_min,
        mock_input_manifest_from_path,
        *mocks
    ):
        mock_tmpdir.__enter__.return_value = "dir"
        mock_component_opensearch_min.return_value = MagicMock(
            name="OpenSearch-Dashboards"
        )
        mock_component_opensearch_min.branches.return_value = ["main", "0.9.0"]
        mock_component_opensearch_min.checkout.return_value = MagicMock(version="0.9.0")
        mock_input_manifest_from_path.return_value = MagicMock(components=[])
        manifests = InputManifestsOpenSearchDashboards()
        manifests.update()
        self.assertEqual(mock_input_manifest().to_file.call_count, 1)
        calls = [
            call(
                os.path.join(
                    InputManifestsOpenSearchDashboards.manifests_path(),
                    "0.9.0/opensearch-dashboards-0.9.0.yml",
                )
            )
        ]
        mock_input_manifest().to_file.assert_has_calls(calls)

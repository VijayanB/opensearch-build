# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

import os
import unittest
from unittest.mock import patch

from build_workflow.build_target import BuildTarget


class TestBuildTarget(unittest.TestCase):
    def test_output_dir(self):
        self.assertEqual(
            BuildTarget(version="1.1.0", arch="x86").output_dir, "artifacts"
        )

    def test_build_id_hex(self):
        self.assertEqual(len(BuildTarget(version="1.1.0", arch="x86").build_id), 32)

    @patch.dict(os.environ, {"OPENSEARCH_BUILD_ID": "id"})
    def test_build_id_from_env(self):
        self.assertEqual(BuildTarget(version="1.1.0", arch="x86").build_id, "id")

    @patch.dict(os.environ, {"OPENSEARCH_DASHBOARDS_BUILD_ID": "id"})
    def test_build_id_from_dashboards_env(self):
        self.assertEqual(BuildTarget(version="1.1.0", arch="x86").build_id, "id")

    def test_build_id_from_arg(self):
        self.assertEqual(
            BuildTarget(version="1.1.0", arch="x86", build_id="id").build_id, "id"
        )

    def test_opensearch_version(self):
        self.assertEqual(
            BuildTarget(version="1.1.0", arch="x86", snapshot=False).opensearch_version,
            "1.1.0",
        )

    def test_opensearch_version_snapshot(self):
        self.assertEqual(
            BuildTarget(version="1.1.0", arch="x86", snapshot=True).opensearch_version,
            "1.1.0-SNAPSHOT",
        )

    def test_component_version(self):
        self.assertEqual(
            BuildTarget(version="1.1.0", arch="x86", snapshot=False).component_version,
            "1.1.0.0",
        )

    def test_component_version_snapshot(self):
        self.assertEqual(
            BuildTarget(version="1.1.0", arch="x86", snapshot=True).component_version,
            "1.1.0.0-SNAPSHOT",
        )

    @patch("build_workflow.build_target.current_arch", return_value="value")
    def test_arch(self, *mock):
        self.assertEqual(BuildTarget(version="1.1.0", snapshot=False).arch, "value")

    def test_arch_value(self):
        self.assertEqual(
            BuildTarget(version="1.1.0", arch="value", snapshot=False).arch, "value"
        )

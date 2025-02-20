# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import yaml

from build_workflow.build_recorder import BuildRecorder
from build_workflow.build_target import BuildTarget
from build_workflow.opensearch.build_artifact_check_maven import \
    BuildArtifactOpenSearchCheckMaven
from build_workflow.opensearch.build_artifact_check_plugin import \
    BuildArtifactOpenSearchCheckPlugin
from manifests.build_manifest import BuildManifest


class TestBuildRecorder(unittest.TestCase):
    def __mock(self, snapshot=True):
        return BuildRecorder(
            BuildTarget(
                build_id="1",
                output_dir="output_dir",
                name="OpenSearch",
                version="1.1.0",
                arch="x64",
                snapshot=snapshot,
            )
        )

    @patch("shutil.copyfile")
    @patch("os.makedirs")
    def test_record_component_and_artifact(self, mock_makedirs, mock_copyfile):
        recorder = self.__mock(snapshot=False)

        recorder.record_component(
            "common-utils",
            MagicMock(
                url="https://github.com/opensearch-project/common-utils",
                ref="main",
                sha="3913d7097934cbfe1fdcf919347f22a597d00b76",
            ),
        )

        recorder.record_artifact("common-utils", "libs", "../file1.jar", __file__)

        recorder.record_artifact("common-utils", "libs", "../file2.jar", __file__)

        self.assertEqual(
            recorder.get_manifest().to_dict(),
            {
                "build": {
                    "architecture": "x64",
                    "id": "1",
                    "name": "OpenSearch",
                    "version": "1.1.0",
                },
                "components": [
                    {
                        "artifacts": {"libs": ["../file1.jar", "../file2.jar"]},
                        "commit_id": "3913d7097934cbfe1fdcf919347f22a597d00b76",
                        "name": "common-utils",
                        "ref": "main",
                        "repository": "https://github.com/opensearch-project/common-utils",
                        "version": "1.1.0.0",
                    }
                ],
                "schema-version": "1.0",
            },
        )

        mock_copyfile.assert_called()
        mock_makedirs.assert_called()

    @patch("shutil.copyfile")
    @patch("os.makedirs")
    def test_record_artifact(self, mock_makedirs, mock_copyfile):
        recorder = self.__mock(snapshot=False)

        recorder.record_component(
            "common-utils",
            MagicMock(
                url="https://github.com/opensearch-project/common-utils",
                ref="main",
                sha="3913d7097934cbfe1fdcf919347f22a597d00b76",
            ),
        )

        recorder.record_artifact("common-utils", "files", "../file1.jar", __file__)

        mock_makedirs.assert_called_with("output_dir/..", exist_ok=True)
        mock_copyfile.assert_called_with(__file__, "output_dir/../file1.jar")

    @patch("shutil.copyfile")
    @patch("os.makedirs")
    def test_record_artifact_check_plugin(self, *mocks):
        recorder = self.__mock(snapshot=False)

        recorder.record_component("security", MagicMock())

        with patch.object(BuildArtifactOpenSearchCheckPlugin, "check") as mock_check:
            recorder.record_artifact(
                "security", "plugins", "../file1.zip", "invalid.file"
            )

        mock_check.assert_called_with("invalid.file")

    @patch("shutil.copyfile")
    @patch("os.makedirs")
    def test_record_artifact_check_maven(self, *mocks):
        recorder = self.__mock(snapshot=False)

        recorder.record_component("security", MagicMock())

        with patch.object(BuildArtifactOpenSearchCheckMaven, "check") as mock_check:
            recorder.record_artifact("security", "maven", "../file1.zip", "valid.jar")

        mock_check.assert_called_with("valid.jar")

    def test_get_manifest(self):
        manifest = self.__mock(snapshot=False).get_manifest()
        self.assertIs(type(manifest), BuildManifest)
        self.assertEqual(
            manifest.to_dict(),
            {
                "build": {
                    "architecture": "x64",
                    "id": "1",
                    "name": "OpenSearch",
                    "version": "1.1.0",
                },
                "schema-version": "1.0",
            },
        )

    def test_write_manifest(self):
        with tempfile.TemporaryDirectory() as dest_dir:
            mock = self.__mock(snapshot=False)
            mock.target.output_dir = dest_dir
            mock.write_manifest()
            manifest_path = os.path.join(dest_dir, "manifest.yml")
            self.assertTrue(os.path.isfile(manifest_path))
            data = mock.get_manifest().to_dict()
            with open(manifest_path) as f:
                self.assertEqual(yaml.safe_load(f), data)

    @patch("shutil.copyfile")
    @patch("os.makedirs")
    @patch.object(BuildArtifactOpenSearchCheckPlugin, "check")
    def test_record_artifact_check_plugin_version_properties(self, *mocks):
        mock = self.__mock(snapshot=False)
        mock.record_component(
            "security",
            MagicMock(
                url="https://github.com/opensearch-project/security",
                ref="main",
                sha="3913d7097934cbfe1fdcf919347f22a597d00b76",
            ),
        )
        mock.record_artifact("security", "plugins", "../file1.zip", "valid-1.1.0.0.zip")
        manifest_dict = mock.get_manifest().to_dict()
        self.assertEqual(manifest_dict["build"]["version"], "1.1.0")
        self.assertEqual(manifest_dict["components"][0]["version"], "1.1.0.0")

    @patch("shutil.copyfile")
    @patch("os.makedirs")
    @patch.object(BuildArtifactOpenSearchCheckPlugin, "check")
    def test_record_artifact_check_plugin_version_properties_snapshot(self, *mocks):
        mock = self.__mock(snapshot=True)
        mock.record_component(
            "security",
            MagicMock(
                url="https://github.com/opensearch-project/security",
                ref="main",
                sha="3913d7097934cbfe1fdcf919347f22a597d00b76",
            ),
        )
        mock.record_artifact(
            "security", "plugins", "../file1.zip", "valid-1.1.0.0-SNAPSHOT.zip"
        )
        manifest_dict = mock.get_manifest().to_dict()
        self.assertEqual(manifest_dict["build"]["version"], "1.1.0-SNAPSHOT")
        self.assertEqual(manifest_dict["components"][0]["version"], "1.1.0.0-SNAPSHOT")

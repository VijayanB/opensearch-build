# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

import unittest
from contextlib import contextmanager
from unittest.mock import patch

from build_workflow.build_artifact_check import BuildArtifactCheck
from build_workflow.build_target import BuildTarget
from build_workflow.opensearch.build_artifact_check_plugin import \
    BuildArtifactOpenSearchCheckPlugin


class TestBuildArtifactOpenSearchCheckPlugin(unittest.TestCase):
    @contextmanager
    def __mock(self, props="", snapshot=True):
        with patch(
            "build_workflow.opensearch.build_artifact_check_plugin.ZipFile"
        ) as mock_zipfile:
            mock_zipfile.return_value.__enter__.return_value.read.return_value.decode.return_value = (
                props
            )
            yield BuildArtifactOpenSearchCheckPlugin(
                BuildTarget(
                    build_id="1",
                    output_dir="output_dir",
                    name="OpenSearch",
                    version="1.1.0",
                    arch="x64",
                    snapshot=snapshot,
                )
            )

    def test_check_plugin_zip_version_snapshot(self):
        with self.assertRaises(BuildArtifactCheck.BuildArtifactInvalidError) as context:
            with self.__mock() as mock:
                mock.check("invalid.zip")
        self.assertEqual(
            "Artifact invalid.zip is invalid. Expected filename to include 1.1.0.0-SNAPSHOT.",
            str(context.exception),
        )

    def test_check_plugin_zip_version(self):
        with self.assertRaises(BuildArtifactCheck.BuildArtifactInvalidError) as context:
            with self.__mock(snapshot=False) as mock:
                mock.check("invalid.zip")
        self.assertEqual(
            "Artifact invalid.zip is invalid. Expected filename to include 1.1.0.0.",
            str(context.exception),
        )

    def test_check_plugin_version_properties_missing(self, *mocks):
        with self.assertRaises(BuildArtifactCheck.BuildArtifactInvalidError) as context:
            with self.__mock("") as mock:
                mock.check("valid-1.1.0.0-SNAPSHOT.zip")
        self.assertEqual(
            "Artifact valid-1.1.0.0-SNAPSHOT.zip is invalid. Expected to have version='1.1.0.0-SNAPSHOT', but none was found.",
            str(context.exception),
        )

    def test_check_plugin_version_properties_mismatch(self, *mocks):
        with self.assertRaises(BuildArtifactCheck.BuildArtifactInvalidError) as context:
            with self.__mock("version=1.2.3.4") as mock:
                mock.check("valid-1.1.0.0-SNAPSHOT.zip")
            self.assertEqual(
                "Artifact valid-1.1.0.0-SNAPSHOT.zip is invalid. Expected to have version='1.1.0.0-SNAPSHOT', but was '1.2.3.4'.",
                str(context.exception),
            )

    def test_check_plugin_version_properties(self, *mocks):
        with self.__mock("opensearch.version=1.1.0\nversion=1.1.0.0-SNAPSHOT") as mock:
            mock.check("valid-1.1.0.0-SNAPSHOT.zip")

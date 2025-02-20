# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

import os
import unittest

import yaml

from manifests.input_manifest import InputManifest


class TestInputManifest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.manifests_path = os.path.realpath(
            os.path.join(os.path.dirname(__file__), "../../manifests")
        )

    def test_1_0(self):
        path = os.path.join(self.manifests_path, "1.0.0/opensearch-1.0.0.yml")
        manifest = InputManifest.from_path(path)
        self.assertEqual(manifest.version, "1.0")
        self.assertEqual(manifest.build.name, "OpenSearch")
        self.assertEqual(manifest.build.version, "1.0.0")
        self.assertEqual(len(manifest.components), 12)
        opensearch_component = manifest.components[0]
        self.assertEqual(opensearch_component.name, "OpenSearch")
        self.assertEqual(
            opensearch_component.repository,
            "https://github.com/opensearch-project/OpenSearch.git",
        )
        self.assertEqual(opensearch_component.ref, "1.0")
        for component in manifest.components:
            self.assertIsInstance(component.ref, str)

    def test_1_1(self):
        path = os.path.join(self.manifests_path, "1.1.0/opensearch-1.1.0.yml")
        manifest = InputManifest.from_path(path)
        self.assertEqual(manifest.version, "1.0")
        self.assertEqual(manifest.build.name, "OpenSearch")
        self.assertEqual(manifest.build.version, "1.1.0")
        self.assertEqual(len(manifest.components), 15)
        # opensearch component
        opensearch_component = manifest.components[0]
        self.assertEqual(opensearch_component.name, "OpenSearch")
        self.assertEqual(
            opensearch_component.repository,
            "https://github.com/opensearch-project/OpenSearch.git",
        )
        self.assertEqual(opensearch_component.ref, "1.1")
        # components
        for component in manifest.components:
            self.assertIsInstance(component.ref, str)
        # alerting component checks
        alerting_component = next(
            c for c in manifest.components if c.name == "alerting"
        )
        self.assertIsNotNone(alerting_component)
        self.assertEqual(len(alerting_component.checks), 2)
        for check in alerting_component.checks:
            self.assertIsInstance(check, InputManifest.Check)
        self.assertIsNone(alerting_component.checks[0].args)
        self.assertEqual(alerting_component.checks[1].args, "alerting")

    def test_to_dict(self):
        path = os.path.join(self.manifests_path, "1.1.0/opensearch-1.1.0.yml")
        manifest = InputManifest.from_path(path)
        data = manifest.to_dict()
        with open(path) as f:
            self.assertEqual(yaml.safe_load(f), data)

    def test_invalid_ref(self):
        data_path = os.path.join(os.path.dirname(__file__), "data")
        manifest_path = os.path.join(data_path, "invalid-ref.yml")

        with self.assertRaises(Exception) as context:
            InputManifest.from_path(manifest_path)
        self.assertEqual(
            "Invalid manifest schema: {'components': [{0: [{'ref': ['must be of string type']}]}]}",
            str(context.exception),
        )

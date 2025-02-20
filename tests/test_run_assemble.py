# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

import os
import tempfile
import unittest
from unittest.mock import MagicMock, call, patch

import pytest

from run_assemble import main


class TestRunAssemble(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def capfd(self, capfd):
        self.capfd = capfd

    @patch("argparse._sys.argv", ["run_assemble.py", "--help"])
    def test_usage(self, *mocks):
        with self.assertRaises(SystemExit):
            main()

        out, _ = self.capfd.readouterr()
        self.assertTrue(out.startswith("usage:"))

    BUILD_MANIFEST = os.path.join(
        os.path.dirname(__file__), "data/opensearch-build-1.1.0.yml"
    )

    @patch("os.chdir")
    @patch("os.makedirs")
    @patch("os.getcwd", return_value="curdir")
    @patch("argparse._sys.argv", ["run_assemble.py", BUILD_MANIFEST])
    @patch("run_assemble.Bundles", return_value=MagicMock())
    @patch("run_assemble.BundleRecorder", return_value=MagicMock())
    @patch("tempfile.TemporaryDirectory")
    @patch("shutil.copy2")
    def test_main(self, mock_copy, mock_temp, mock_recorder, mock_bundles, *mocks):
        mock_temp.return_value.__enter__.return_value = tempfile.gettempdir()
        mock_bundle = MagicMock(archive_path="path")
        mock_bundles.create.return_value = mock_bundle

        main()

        mock_bundle.install_plugins.assert_called()

        mock_copy.assert_called_with(
            os.path.realpath(
                os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "../scripts/legacy/tar/linux/opensearch-tar-install.sh",
                )
            ),
            "path/opensearch-tar-install.sh",
        )

        mock_bundle.build_tar.assert_called_with("curdir/bundle")

        mock_recorder.return_value.write_manifest.assert_has_calls(
            [call("path"), call("curdir/bundle")]  # manifest included in tar
        )

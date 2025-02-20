import argparse
import os
import sys

import yaml

from git.git_repository import GitRepository
from manifests.bundle_manifest import BundleManifest
from system.temporary_directory import TemporaryDirectory
from system.working_directory import WorkingDirectory
from test_workflow.perf_test.perf_test_cluster import PerfTestCluster
from test_workflow.perf_test.perf_test_suite import PerfTestSuite

"""
    Entry point for Performance Test with bundle manifest, config file containing the required arguments for running
    rally test and the stack name for the cluster. Will call out in test.sh with perf as argument
"""


parser = argparse.ArgumentParser(description="Test an OpenSearch Bundle")
parser.add_argument(
    "--bundle-manifest", type=argparse.FileType("r"), help="Bundle Manifest file."
)
parser.add_argument("--stack", dest="stack", help="Stack name for performance test")
parser.add_argument("--config", type=argparse.FileType("r"), help="Config file.")
parser.add_argument(
    "--keep",
    dest="keep",
    action="store_true",
    help="Do not delete the working temporary directory.",
)
args = parser.parse_args()

manifest = BundleManifest.from_file(args.bundle_manifest)

config = yaml.safe_load(args.config)


def get_infra_repo_url():
    if "GITHUB_TOKEN" in os.environ:
        return "https://${GITHUB_TOKEN}@github.com/opensearch-project/opensearch-infra.git"
    return "https://github.com/opensearch-project/opensearch-infra.git"


def main():
    with TemporaryDirectory(keep=args.keep) as work_dir:
        os.chdir(work_dir)
        current_workspace = os.path.join(work_dir, 'infra')
        GitRepository(get_infra_repo_url(), "main", current_workspace)
        security = False
        for component in manifest.components:
            if component.name == "security":
                security = True

        with WorkingDirectory(current_workspace):
            with PerfTestCluster.create(manifest, config, args.stack, security, current_workspace) as (
                test_cluster_endpoint,
                test_cluster_port,
            ):
                os.chdir(current_workspace)
                perf_test_suite = PerfTestSuite(
                    manifest, test_cluster_endpoint, security, current_workspace
                )
                perf_test_suite.execute()


if __name__ == "__main__":
    sys.exit(main())

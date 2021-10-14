#!/usr/bin/env python

# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

import argparse
import logging
import os
import sys

from manifests.build_manifest import BuildManifest
from sign_workflow.signer import Signer
from system import console


def main():
    parser = argparse.ArgumentParser(description="Sign stand-alone component artifacts")
    parser.add_argument("--component", nargs="?", help="Component name")
    parser.add_argument(
        "-v",
        "--verbose",
        help="Show more verbose output.",
        action="store_const",
        default=logging.INFO,
        const=logging.DEBUG,
        dest="logging_level",
    )
    args = parser.parse_args()

    console.configure(level=args.logging_level)
    signer = Signer()

    for component in manifest.components:

        if args.component and args.component != component.name:
            logging.info(f"Skipping {component.name}")
            continue

        logging.info(f"Signing {component.name}")
        for artifact_type in component.artifacts:

            if args.type and args.type != artifact_type:
                continue

            signer.sign_artifacts(component.artifacts[artifact_type], basepath)

    logging.info("Done.")


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env bash
set -euo pipefail

# The bench currently has system pytest plus user-site plugins that can be
# version-mismatched. Keep repo tests deterministic by disabling plugin autoload.
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q "$@"


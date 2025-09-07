#!/bin/bash

set -e

# This was the version provided during artifact evaluation.
VERSION=138.0.7204.92

while [[ $# -gt 0 ]]; do
  case "$1" in
    -v)
      VERSION="$2"
      shift 2
      ;;
    *)
      echo "Usage: $0 [--v <version|latest>]"
      exit 1
      ;;
  esac
done

git clone https://github.com/wspr-ncsu/visiblev8.git
cd visiblev8/builder

if [ "$VERSION" = "latest" ]; then
  make webview
else
  make webview VERSION="$VERSION"
fi

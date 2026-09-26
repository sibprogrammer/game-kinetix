#!/usr/bin/env bash

set -euo pipefail

project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$project_root"

if [[ "$(uname)" != "Darwin" ]]; then
  echo "macOS is required to build the application DMG." >&2
  exit 1
fi

artifact_label="${1:-local}"

uv run --locked pyinstaller \
  --clean \
  --noconfirm \
  --windowed \
  --name Kinetix \
  --icon "${project_root}/images/app_icon.icns" \
  --workpath build/pyinstaller \
  --specpath build \
  --add-data "${project_root}/images:images" \
  --add-data "${project_root}/fonts:fonts" \
  --add-data "${project_root}/levels:levels" \
  --add-data "${project_root}/music:music" \
  --add-data "${project_root}/sounds:sounds" \
  main.py

hdiutil create \
  -volname Kinetix \
  -srcfolder dist/Kinetix.app \
  -ov \
  -format UDZO \
  "dist/Kinetix-${artifact_label}.dmg"

echo "Created dist/Kinetix-${artifact_label}.dmg"

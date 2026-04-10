#!/bin/bash
# install.sh — sets up claude-usage-statusline in ~/.claude/settings.json

set -e

PLUGIN_DIR="$(cd "$(dirname "$0")" && pwd)"
SETTINGS="$HOME/.claude/settings.json"

echo "Installing claude-usage-statusline..."

# Check Python 3 is available
if ! command -v python3 &>/dev/null; then
  echo "Error: python3 is required but not found."
  exit 1
fi

# Add statusLine config to settings.json
python3 - "$SETTINGS" "$PLUGIN_DIR" <<'EOF'
import json, sys, os

settings_path = sys.argv[1]
plugin_dir = sys.argv[2]
script_path = os.path.join(plugin_dir, "usage.py")

# Load existing settings
try:
    with open(settings_path) as f:
        settings = json.load(f)
except FileNotFoundError:
    settings = {}

# Don't overwrite if already configured
if "statusLine" in settings:
    print(f"statusLine already configured in {settings_path} — skipping.")
    print("To reconfigure, remove the 'statusLine' key and re-run install.sh.")
    sys.exit(0)

settings["statusLine"] = {
    "type": "command",
    "command": f"python3 {script_path}",
    "refreshInterval": 60
}

os.makedirs(os.path.dirname(settings_path), exist_ok=True)
with open(settings_path, "w") as f:
    json.dump(settings, f, indent=2)
    f.write("\n")

print(f"Done! statusLine configured in {settings_path}")
print(f"Restart Claude Code to see the status line.")
EOF

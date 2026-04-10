# claude-usage-statusline

A Claude Code status line plugin that shows your token usage and rate limits — matching exactly what you see on the [claude.ai](https://claude.ai) dashboard.

## Preview

```
281k tokens today · 456k tokens this week · billing resets in 21d  │  ███████░░░ 73% session resets 2h12m  │  ██████░░░░ 56% week resets 1h12m
```

| Segment | What it shows |
|---|---|
| `281k tokens today` | Tokens used across all Claude Code sessions today |
| `456k tokens this week` | Rolling 7-day token total |
| `billing resets in 21d` | Days until your monthly billing cycle resets |
| `███████░░░ 73% session` | Current session rate limit — matches dashboard "Current session" |
| `██████░░░░ 56% week` | 7-day rate limit — matches dashboard "Weekly limits" |

**Color coding:**
- 🟢 Green — 0–74% (normal)
- 🟡 Yellow — 75–89% (getting full)
- 🔴 Red — 90–100% (critical)

## Requirements

- [Claude Code](https://claude.ai/code) CLI
- Python 3 (pre-installed on macOS/Linux)

## Installation

### Option 1 — Auto install (recommended)

```bash
git clone https://github.com/hein/claude-usage-statusline ~/.claude/plugins/claude-usage-statusline
cd ~/.claude/plugins/claude-usage-statusline
chmod +x install.sh
./install.sh
```

Restart Claude Code — the status line appears automatically.

### Option 2 — Manual install

1. Clone the repo anywhere:
   ```bash
   git clone https://github.com/hein/claude-usage-statusline ~/claude-usage-statusline
   ```

2. Add to `~/.claude/settings.json`:
   ```json
   {
     "statusLine": {
       "type": "command",
       "command": "python3 ~/claude-usage-statusline/usage.py",
       "refreshInterval": 60
     }
   }
   ```

3. Restart Claude Code.

## Configuration

### Custom billing reset day

By default the billing reset countdown targets the **1st of each month**. If your plan resets on a different day, set the `CLAUDE_USAGE_RESET_DAY` environment variable:

```bash
# Add to ~/.zshrc or ~/.bashrc
export CLAUDE_USAGE_RESET_DAY=15   # resets on the 15th
```

## How it works

- **Token counts** — reads `~/.claude/projects/*/` JSONL session files and sums `input_tokens + output_tokens` for today/this week. Updates in real time.
- **Progress bars** — read from the JSON Claude Code pipes to the status line script on each update. Same data source as the claude.ai dashboard.
- **Billing reset** — calculated from today's date and `CLAUDE_USAGE_RESET_DAY`.

## License

MIT

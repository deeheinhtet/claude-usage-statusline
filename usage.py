#!/usr/bin/env python3
"""
Claude Code usage status line script.
Reads JSON from stdin (Claude Code session data) and ~/.claude/stats-cache.json.
Matches claude.ai dashboard: Current session (5h limit) + Weekly limits (7d limit).
Prints: "42k today · 280k this week · resets in 21d  │  ███████░░░ 73% session resets 2h12m  │  █████░░░░░ 56% week resets 1h12m"
"""
import json
import os
import sys
import time
from datetime import date, timedelta
from pathlib import Path


STATS_CACHE = Path.home() / ".claude" / "stats-cache.json"
RESET_DAY = int(os.environ.get("CLAUDE_USAGE_RESET_DAY", "1"))


def format_tokens(n: int) -> str:
    """Format token count as '42k tokens'."""
    if n >= 1000:
        return f"{round(n / 1000)}k tokens"
    return f"{n} tokens"


def make_bar(pct: float) -> str:
    """Return a colored 10-char Unicode block bar with percentage label."""
    pct = max(0.0, min(100.0, float(pct)))
    filled = round(pct / 10)
    empty = 10 - filled
    bar = "\u2588" * filled + "\u2591" * empty
    if pct >= 90:
        color = "\033[31m"   # red
    elif pct >= 75:
        color = "\033[33m"   # yellow
    else:
        color = "\033[32m"   # green
    return f"{color}{bar}\033[0m {round(pct)}%"


def days_until_reset(reset_day: int) -> int:
    """Days until the next billing reset day (e.g. 1st of month)."""
    import calendar
    today = date.today()

    try:
        reset_this_month = today.replace(day=reset_day)
    except ValueError:
        last_day = calendar.monthrange(today.year, today.month)[1]
        reset_this_month = today.replace(day=last_day)

    if reset_this_month > today:
        return (reset_this_month - today).days

    if today.month == 12:
        next_month_year, next_month = today.year + 1, 1
    else:
        next_month_year, next_month = today.year, today.month + 1

    try:
        reset_next_month = date(next_month_year, next_month, reset_day)
    except ValueError:
        last_day = calendar.monthrange(next_month_year, next_month)[1]
        reset_next_month = date(next_month_year, next_month, last_day)

    return (reset_next_month - today).days


def load_stats() -> dict:
    """Load stats-cache.json. Returns empty dict on any error."""
    try:
        return json.loads(STATS_CACHE.read_text())
    except Exception:
        return {}


def get_daily_tokens(stats: dict, target_date: str) -> int:
    """Sum all model tokens for a given date string (YYYY-MM-DD)."""
    for entry in stats.get("dailyModelTokens", []):
        if entry.get("date") == target_date:
            return sum(entry.get("tokensByModel", {}).values())
    return 0


def get_weekly_tokens(stats: dict) -> int:
    """Sum tokens for the past 7 days (rolling window)."""
    today = date.today()
    dates = {(today - timedelta(days=i)).isoformat() for i in range(7)}
    total = 0
    for entry in stats.get("dailyModelTokens", []):
        if entry.get("date") in dates:
            total += sum(entry.get("tokensByModel", {}).values())
    return total


def format_reset_time(resets_at_epoch) -> str:
    """Format seconds until reset as '2h12m' or '45m' or '--'."""
    if not resets_at_epoch:
        return "--"
    secs = int(resets_at_epoch) - int(time.time())
    if secs <= 0:
        return "now"
    mins = secs // 60
    hours = mins // 60
    remaining_mins = mins % 60
    if hours > 0:
        return f"{hours}h{remaining_mins:02d}m"
    return f"{mins}m"


def main():
    # Parse stdin JSON from Claude Code
    session = {}
    try:
        session = json.loads(sys.stdin.read())
    except Exception:
        pass

    rate_limits = session.get("rate_limits", {})

    # Match dashboard: "Current session" = 5-hour limit, "Weekly limits" = 7-day limit
    session_pct = rate_limits.get("five_hour", {}).get("used_percentage", 0) or 0
    session_resets_at = rate_limits.get("five_hour", {}).get("resets_at")
    week_pct = rate_limits.get("seven_day", {}).get("used_percentage", 0) or 0
    week_resets_at = rate_limits.get("seven_day", {}).get("resets_at")

    stats = load_stats()
    if not stats:
        print("Usage data unavailable")
        return

    today_str = date.today().isoformat()
    today_tokens = get_daily_tokens(stats, today_str)
    week_tokens = get_weekly_tokens(stats)
    reset_days = days_until_reset(RESET_DAY)

    left = (
        f"{format_tokens(today_tokens)} today "
        f"\u00b7 {format_tokens(week_tokens)} this week "
        f"\u00b7 resets in {reset_days}d"
    )
    session_bar = make_bar(session_pct)
    week_bar = make_bar(week_pct)
    session_reset_str = format_reset_time(session_resets_at)
    week_reset_str = format_reset_time(week_resets_at)

    print(
        f"{left}  \u2502  "
        f"{session_bar} session resets {session_reset_str}  \u2502  "
        f"{week_bar} week resets {week_reset_str}"
    )


if __name__ == "__main__":
    main()

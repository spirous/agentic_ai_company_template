#!/bin/zsh
# setup-cron.sh — Install the weekly Contact Intelligence review as a cron job.
#
# Schedule: Every Monday at 08:00 local time.
# Output:   Publishes "📊 Contact Intelligence Dashboard" in Confluence
#           + macOS desktop notification.
#
# Run once:  zsh scripts/setup-cron.sh
# Remove:    zsh scripts/setup-cron.sh --remove

set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON="$(which python3)"
SCRIPT="$PROJECT_DIR/scripts/weekly_review.py"
LOG="$PROJECT_DIR/logs/weekly_review.log"
CRON_TAG="# agentic-company weekly-contact-review"

CRON_LINE="0 8 * * 1 cd \"$PROJECT_DIR\" && $PYTHON \"$SCRIPT\" >> \"$LOG\" 2>&1 $CRON_TAG"

mkdir -p "$PROJECT_DIR/logs"

if [[ "$1" == "--remove" ]]; then
  crontab -l 2>/dev/null | grep -v "$CRON_TAG" | crontab -
  echo "✅ Weekly review cron job removed."
  exit 0
fi

if crontab -l 2>/dev/null | grep -q "$CRON_TAG"; then
  echo "ℹ️  Weekly review cron job already installed."
  echo "   To reinstall: run --remove first, then run again."
  exit 0
fi

(crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -

echo "✅ Weekly review cron job installed."
echo "   Schedule: Every Monday at 08:00"
echo "   Script:   $SCRIPT"
echo "   Log:      $LOG"
echo ""
echo "   Run now to test: python3 $SCRIPT --dry-run"
echo "   Remove:          zsh $0 --remove"

#!/usr/bin/env bash
# Interactive first-time setup for the agentic company workspace.

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_DIR/.env"

echo ""
echo "=== Agentic Company Workspace — Setup ==="
echo ""

read -rp "Company name (used in filenames and logs): " COMPANY_NAME
read -rp "Your email address: " USER_EMAIL
read -rp "Confluence URL (e.g. https://yourcompany.atlassian.net): " CONFLUENCE_URL
read -rp "Confluence space key (e.g. MKTG): " CONFLUENCE_SPACE
read -rp "Confluence default parent page title: " CONFLUENCE_DEFAULT_PARENT
read -rp "Anthropic API key (leave blank to skip): " ANTHROPIC_API_KEY

cat > "$ENV_FILE" <<EOF
# Company
COMPANY_NAME=$COMPANY_NAME
USER_EMAIL=$USER_EMAIL

# Confluence
CONFLUENCE_URL=$CONFLUENCE_URL
CONFLUENCE_EMAIL=$USER_EMAIL
CONFLUENCE_SPACE=$CONFLUENCE_SPACE
CONFLUENCE_DEFAULT_PARENT=$CONFLUENCE_DEFAULT_PARENT

# Anthropic (optional — for cloud inference)
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
EOF

echo "✅ .env written to $ENV_FILE"

IDENTITY_FILE="$PROJECT_DIR/company/identity.md"
if grep -q "\[Company Name\]" "$IDENTITY_FILE" 2>/dev/null; then
    sed -i.bak "s/\[Company Name\]/$COMPANY_NAME/g" "$IDENTITY_FILE" && rm "$IDENTITY_FILE.bak"
    echo "✅ company/identity.md updated"
fi

echo ""
read -rp "Add scripts/ to PATH in ~/.zshrc? (y/n): " ADD_PATH
if [[ "$ADD_PATH" == "y" ]]; then
    echo "export PATH=\"\$PATH:$SCRIPT_DIR\"" >> ~/.zshrc
    echo "✅ Added to ~/.zshrc — run: source ~/.zshrc"
fi

echo ""
echo "=== Setup complete ==="
echo "Next: fill in company/identity.md and company/style/style.md"
echo ""

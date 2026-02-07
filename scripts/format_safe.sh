#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# Always-safe whitespace normalization.
find . \
  -type f \
  \( -name "*.md" -o -name "*.tex" -o -name "*.py" -o -name "*.yaml" -o -name "*.yml" -o -name "*.sh" -o -name "Makefile" -o -name ".editorconfig" -o -name ".gitignore" \) \
  -not -path "./.git/*" \
  -exec sed -i 's/[[:space:]]*$//' {} +

# Optional LaTeX indentation if latexindent is available.
if command -v latexindent >/dev/null 2>&1; then
  while IFS= read -r tex_file; do
    latexindent -w "$tex_file" >/dev/null 2>&1 || true
    rm -f "${tex_file}.bak"
  done < <(find docs/derivations -type f -name "*.tex" | sort)
fi

echo "safe formatting complete"

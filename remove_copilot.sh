#!/bin/sh
# Script to remove GitHub Copilot from git history

# Rewrite all commits that have GitHub Copilot as author/committer
git filter-branch --env-filter '
if [ "$GIT_AUTHOR_NAME" = "GitHub Copilot" ] || [ "$GIT_AUTHOR_NAME" = "Copilot" ] || [ "$GIT_AUTHOR_NAME" = "copilot-swe-agent[bot]" ]; then
    export GIT_AUTHOR_NAME="Rahul Joshi"
    export GIT_AUTHOR_EMAIL="rahuljoshi07@example.com"
fi
if [ "$GIT_COMMITTER_NAME" = "GitHub Copilot" ] || [ "$GIT_COMMITTER_NAME" = "Copilot" ] || [ "$GIT_COMMITTER_NAME" = "copilot-swe-agent[bot]" ]; then
    export GIT_COMMITTER_NAME="Rahul Joshi"
    export GIT_COMMITTER_EMAIL="rahuljoshi07@example.com"
fi
' --tag-name-filter cat -- --all

echo "Git history has been rewritten. Use 'git push -f origin main' to update the repository."

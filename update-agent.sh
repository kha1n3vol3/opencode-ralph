# brew install bd
brew upgrade steveyegge/beads/bd
brew upgrade pnpm
brew upgrade gh
brew upgrade ruff
brew upgrade uv
# Track, sync & share AI coding sessions across your team. Context that survives beyond the chat. Stop re-explaining yourself every session. Currently works with Claude Code.

# pnpm install -g grov

# agents cli
pnpm approve-builds -g
# pnpm install -g @google/gemini-cli
pnpm install -g @google/gemini-cli@latest
pnpm install -g @anthropic-ai/claude-code@latest
pnpm install -g @openai/codex@latest

bd doctor --fix 
bd onboard

Echo tell your AI assistant: "run terminal command; bd onboarding complete"

echo "Done!"
echo "gemini --model gemini-3-flash-preview"


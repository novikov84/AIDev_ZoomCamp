Agent notes
-----------

- Work locally in `Assignment_2/`. Keep edits focused and commit early/often (e.g., after scaffolding, tests, dev scripts, syntax highlighting, execution, docker, deploy docs).
- Default git flow:
  1. `git status` to review changes.
  2. `git add <files>` for the current step.
  3. `git commit -m "clear, scoped message"`; avoid amending user commits.
  4. `git push` when ready (user controls remote).
- Environment: target Python 3.11 via conda + `uv` for deps; npm for frontend. Prefer reproducible commands and pin versions.
- References: follow the AI Dev Tools Zoomcamp patterns (02-end-to-end) for structuring README commands, dev scripts, testing, and Docker/Render deployment sections.
- When running commands, stay within workspace and avoid destructive actions (`git reset --hard`, force pushes) unless the user explicitly asks.

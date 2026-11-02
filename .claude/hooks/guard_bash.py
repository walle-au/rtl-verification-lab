#!/usr/bin/env python3
"""PreToolUse hook: blocks dangerous or forbidden Bash commands.

Claude Code sends the tool call as JSON on stdin. Exit code 2 cancels the
action and the message on stderr is shown to the agent as the reason.
"""

import json
import re
import sys

RULES = [
    (r"\bgit\s+(commit|push)\b", "El usuario hace todos los commits y push. Sugiere el comando en vez de ejecutarlo."),
    (r"\bgh\s+(repo\s+create|pr\s+create|pr\s+merge)\b", "Crear repos o PRs lo hace el usuario."),
    (r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f|\brm\s+-[a-zA-Z]*f[a-zA-Z]*r", "rm -rf está bloqueado en este proyecto."),
    (r"\bgit\s+(reset\s+--hard|clean\s+-[a-zA-Z]*f)", "Comando git destructivo bloqueado."),
]

data = json.load(sys.stdin)
command = data.get("tool_input", {}).get("command", "")

for pattern, reason in RULES:
    if re.search(pattern, command):
        print(f"Bloqueado por hook: {reason}", file=sys.stderr)
        sys.exit(2)

sys.exit(0)

#!/bin/zsh
set -e
TASK_ROOT="$HOME/AIVideoLocal/maemorkratai"
if [[ ! -x "$TASK_ROOT/.venv/bin/python" ]]; then
  print "ยังไม่มี runtime อ่านคู่มือใน MaeMorKratai/README.md ก่อน"
  exit 1
fi
cd "$TASK_ROOT"
exec "$TASK_ROOT/.venv/bin/python" scripts/open_center.py

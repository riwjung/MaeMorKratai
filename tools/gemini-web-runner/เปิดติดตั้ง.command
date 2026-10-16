#!/bin/zsh
set -eu
runner_dir="$(cd "$(dirname "$0")" && pwd)"
open -R "$runner_dir/extension/manifest.json"
open -a "Google Chrome" "chrome://extensions/"
open -a "Google Chrome" "https://gemini.google.com/u/0/app/c1051ca2e5090320"
printf '\nเลือก Load unpacked แล้วเลือกโฟลเดอร์ extension ที่เปิดไว้ จากนั้นรีเฟรชแชท Gemini\n'

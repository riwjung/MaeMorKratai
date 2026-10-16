#!/bin/zsh
set -euo pipefail
cd /Users/sawettachatsuthum/AIVideoLocal/maemorkratai/halloween-2026
ffprobe -v error -show_streams -show_format -of json renders/MaeMorKratai_Halloween_2026_v3.mp4 > probe.json
ffmpeg -hide_banner -i renders/MaeMorKratai_Halloween_2026_v3.mp4 -vf 'blackdetect=d=0.02:pix_th=0.1:pic_th=0.98' -f null - > decode-check.log 2>&1
ffmpeg -v error -y -i renders/MaeMorKratai_Halloween_2026_v3.mp4 -vf 'fps=1,scale=270:480,tile=4x3' -frames:v 1 renders/encoded-contact-sheet.jpg
ffmpeg -v error -y -ss 10.6 -i renders/MaeMorKratai_Halloween_2026_v3.mp4 -frames:v 1 renders/encoded-hero.png
/Users/sawettachatsuthum/AIVideoLocal/maemorkratai/.venv/bin/python check_playback.py

# Verification — 2026-10-15

Original purple-home endcard: 10.000s,1080×1920,30fps,300frames,H.264 High,yuv420p,bt709,no audio.

Preflight passed; HyperFrames0.8.140 lint0errors0warnings. Runtime and contrast checks passed. Two SVG clipping/layout warnings plus one informational finding were visually triaged: source bitmap bounds exceed its silhouette mask and the paw translates while rotating at its wrist. No visible content cropped at the output edges.

Studio playback/iframe verified (studio-audit.json); encoded playback ended normally,Range206,10s,1080×1920,300frames,no browser errors; preview responsive at390px (playback-check.json). Encoded contact sheet at2fps and8.8s hero inspected. Full decode and blackdetect found no black interval. Silent by design. No credits spent.

# MaeMorKratai Halloween 2026

HyperFrames + GSAP, 1080×1920, 30fps, 12s, silent. Original MMKT_Hallow.JPG retained byte-for-byte in assets/character.jpg and clipped in SVG. Scene uses CSS 3D layers; no regenerated face or 3D character mesh. All assets local, no paid calls.

Build: `python build_scene.py`
Preview: `hyperframes preview .` or `python preview_server.py` (127.0.0.1:3004, needs FastAPI/uvicorn).
Render: `hyperframes render . --output renders/MaeMorKratai_Halloween_2026_v3.mp4 --fps 30 --quality high --workers 2 --strict --no-best-effort --no-browser-gpu`

Text, duration and palette live in build_scene.py / DESIGN.md. Edit the builder and rebuild. Original image belongs to the project owner; bundled Georgia is for local project rendering, not a public font distribution. See VERIFY.md for actual checks.

## V2: shuffle and show
Owner approved the scene and requested the previous endcard's shuffle gesture.
The original raster paws are now clipped into articulated layers; only the hidden chest underneath is reconstructed using SVG. Three coordinated shuffles, consolidation, draw, face flip and hold. The original face, hat, costume edges, feet and surrounding room remain from v1.
Current export: renders/MaeMorKratai_Halloween_2026_v3.mp4.
V1 MP4 and build_scene_v1.py are retained for comparison. Current builder produces v3; build_scene_v2.py preserves v2.

## V3: blinking eyes
Added four brief blinks using local texture eyelids, preserving the v2 shuffle/show routine. See VERIFY.md and check-v3.json. This is the scene reused by the tarot web prototype.

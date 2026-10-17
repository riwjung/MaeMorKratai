'use client';
import {useEffect, useRef} from 'react';
import type * as Three from 'three';
import {loadReadingMotion} from '../../lib/reading-motion';
import {fanArc, FAN_STEP} from './fan';

// WebGL deck for shuffle → gather → spread. The shuffle follows the Moonlight-style loop: the deck turns
// on its own axis while each card travels a vertical loop around it, top card first, staying upright.
// Every card keeps the same orientation as every other card (only an in-plane tilt differs), so cards
// never cut through each other; they only pass in front of or behind one another.
// The DOM fan stays the selectable, accessible deck; the spread lands pixel-exact on it and hands over.
const CARDS = 78; // cards in the fan
const SHUFFLE = 30; // cards that travel during the shuffle; the rest of the deck joins at the spread
const DEPTH = 1400; // camera distance; the z = 0 plane maps 1 world unit to 1 CSS px
const CYCLE = 3; // seconds for one loop of a card
const STAGGER = .1; // seconds between neighbouring cards; SHUFFLE × STAGGER = one CYCLE, so the ring is evenly spaced
const INTRO = .35; // seconds to settle from the flat placeholder into the tilted deck
const GAP = .0133; // resting stack spacing, in card widths
const PUSH = .14; // loop radius every card gets while shuffling
const RING_GAP = .0115; // extra loop radius per card while shuffling, so neighbouring loops stay apart
const LIFT = .4; // up/down travel of each card during its loop
const THICK = .008; // card thickness, so a deck turned side-on still shows its edges
const TILT = -.1745; // 10° back, so the edges of the stack show at the bottom
const REST_YAW = -.22;
const SPIN = 4; // seconds per turn of the whole deck
const GATHER = .9;
const SPREAD = 1.15;
const FAN_DEPTH = 1;

export type DeckPhase = 'shuffling' | 'gathering' | 'spreading' | 'selecting';
const TAU = Math.PI * 2;
const sineInOut = (x: number) => (1 - Math.cos(Math.PI * Math.min(Math.max(x, 0), 1))) / 2;
const inOut = (x: number) => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
const outQuart = (x: number) => 1 - Math.pow(1 - x, 4);
const outCubic = (x: number) => 1 - Math.pow(1 - Math.min(Math.max(x, 0), 1), 3);
const LIFT_KEYS = [0, 1, -1, 0];

// One card's place on its loop at local time `tau` (seconds since that card started).
function loop(tau: number) {
  if (tau <= 0) return {turn: 0, lift: 0};
  const s = tau / CYCLE - Math.floor(tau / CYCLE);
  const third = Math.min(Math.floor(s * 3), 2), f = s * 3 - third;
  return {turn: TAU * sineInOut(s), lift: LIFT_KEYS[third] + (LIFT_KEYS[third + 1] - LIFT_KEYS[third]) * sineInOut(f)};
}

function cardGeometry(THREE: typeof Three) {
  const r = .058, w = .5, h = .8; // corner radius from card-back.svg (35 / 600)
  const shape = new THREE.Shape();
  shape.moveTo(-w + r, -h); shape.lineTo(w - r, -h); shape.quadraticCurveTo(w, -h, w, -h + r);
  shape.lineTo(w, h - r); shape.quadraticCurveTo(w, h, w - r, h); shape.lineTo(-w + r, h);
  shape.quadraticCurveTo(-w, h, -w, h - r); shape.lineTo(-w, -h + r); shape.quadraticCurveTo(-w, -h, -w + r, -h);
  const geometry = new THREE.ExtrudeGeometry(shape, {depth: THICK, bevelEnabled: false, curveSegments: 5});
  geometry.translate(0, 0, -THICK / 2);
  // Map the card art onto both faces; the back face is mirrored so it reads the right way round.
  const position = geometry.attributes.position, uv = geometry.attributes.uv, caps = geometry.groups[0];
  for (let k = caps.start; k < caps.start + caps.count; k++) {
    const x = position.getX(k), y = position.getY(k);
    uv.setXY(k, position.getZ(k) < 0 ? .5 - x : x + .5, (y + h) / (2 * h));
  }
  uv.needsUpdate = true;
  return geometry;
}

export function DeckScene({phase, onFail, onGathered, onSpread}: {phase: DeckPhase; onFail: ()=>void; onGathered: ()=>void; onSpread: ()=>void}) {
  const phaseRef = useRef(phase); phaseRef.current = phase;
  const calls = useRef({onFail, onGathered, onSpread}); calls.current = {onFail, onGathered, onSpread};
  useEffect(()=>{
    let disposed = false;
    const teardown: (()=>void)[] = [];
    const release = () => teardown.splice(0).reverse().forEach(run => run());
    const fail = () => {if (!disposed) calls.current.onFail();};
    // Stays mounted through 'selecting' only to fade out over the DOM fan; never starts a deck there.
    if (phaseRef.current === 'selecting') return;
    // A slow connection should not hold the ritual: fall back to the DOM deck if WebGL is not live in time.
    let live = false;
    const slow = setTimeout(() => {if (!live) fail();}, 4000);
    teardown.push(() => clearTimeout(slow));
    Promise.all([import('three'), loadReadingMotion().catch(()=>null)]).then(([THREE, motion]) => {
      if (disposed) return;
      let renderer: Three.WebGLRenderer;
      try {renderer = new THREE.WebGLRenderer({antialias: true, alpha: true, powerPreference: 'high-performance'});}
      catch {fail(); return;}
      teardown.push(() => {renderer.dispose(); renderer.domElement.remove();});
      const canvas = renderer.domElement;
      canvas.className = 'ritual-deck-canvas';
      canvas.setAttribute('aria-hidden', 'true');
      renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
      renderer.outputColorSpace = THREE.SRGBColorSpace;
      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(40, 1, 10, 6000);
      camera.position.set(0, 0, DEPTH);
      const resize = () => {
        renderer.setSize(innerWidth, innerHeight);
        camera.aspect = innerWidth / innerHeight;
        camera.fov = 2 * Math.atan(innerHeight / 2 / DEPTH) * 180 / Math.PI;
        camera.updateProjectionMatrix();
      };
      resize();
      addEventListener('resize', resize);
      teardown.push(() => removeEventListener('resize', resize));
      // A gentle tilt toward the mouse, as on the reference; touch input leaves the deck still.
      const lean = {x: 0, y: 0, tx: 0, ty: 0};
      const pointer = (event: PointerEvent) => {
        if (event.pointerType !== 'mouse') return;
        lean.tx = -(event.clientY / innerHeight - .5) * .17;
        lean.ty = (event.clientX / innerWidth - .5) * .35;
      };
      addEventListener('pointermove', pointer);
      teardown.push(() => removeEventListener('pointermove', pointer));

      const geometry = cardGeometry(THREE);
      const edge = new THREE.MeshBasicMaterial({color: 0xe3c8b4});
      teardown.push(() => {geometry.dispose(); edge.dispose();});
      const deck = new THREE.Group();
      scene.add(deck);
      const meshes: Three.Mesh[] = [], tints: Three.Color[] = [];
      const jitter = Array.from({length: CARDS}, (_, i) => i === SHUFFLE - 1 ? 0 : (Math.random() - .5) * .09);
      const centre = (SHUFFLE - 1) / 2 * GAP;

      const blob = document.createElement('canvas');
      blob.width = blob.height = 128;
      const ctx = blob.getContext('2d');
      if (ctx) {
        const glow = ctx.createRadialGradient(64, 64, 0, 64, 64, 64);
        glow.addColorStop(0, 'rgba(6,3,13,.7)'); glow.addColorStop(1, 'rgba(6,3,13,0)');
        ctx.fillStyle = glow; ctx.fillRect(0, 0, 128, 128);
      }
      const shadowMap = new THREE.CanvasTexture(blob);
      const shadowMaterial = new THREE.MeshBasicMaterial({map: shadowMap, transparent: true, depthWrite: false});
      const shadowPlane = new THREE.PlaneGeometry(1, 1);
      const shadow = new THREE.Mesh(shadowPlane, shadowMaterial);
      scene.add(shadow);
      teardown.push(() => {shadowMap.dispose(); shadowMaterial.dispose(); shadowPlane.dispose();});

      const anchor = () => document.querySelector<HTMLElement>('.ritual-shuffle');
      const toWorld = (x: number, y: number, z: number) => {const k = (DEPTH - z) / DEPTH; return {p: new THREE.Vector3((x - innerWidth / 2) * k, (innerHeight / 2 - y) * k, z), k};};
      const identity = new THREE.Quaternion(), zAxis = new THREE.Vector3(0, 0, 1), white = new THREE.Color(1, 1, 1);
      const turnQ = new THREE.Quaternion(), baseQ = new THREE.Quaternion();
      let mode: 'shuffle' | 'gather' | 'held' | 'spread' | 'done' = 'shuffle';
      let clock = 0, last = -1, start = -1;
      // The deck's own pose; per card: height and depth on the deck's vertical plane.
      const pose = {yaw: 0, pitch: 0, settle: 0, y: new Float32Array(SHUFFLE), z: new Float32Array(SHUFFLE)};
      const from = {yaw: 0, pitch: 0, spin: 0, y: new Float32Array(SHUFFLE), z: new Float32Array(SHUFFLE), yawTo: 0, yawTime: 1};
      let plan: {base: Three.Quaternion; start: {p: Three.Vector3; s: number; tilt: number}[]; mid: {p: Three.Vector3; s: number}[]; end: {p: Three.Vector3; s: number; r: number}[]; clip: [number, number, number]; fan: {left: number; top: number}} | null = null;

      function spinAngle(t: number) {
        // Starts turning shortly after the cards begin, easing up to a steady turn every SPIN seconds.
        const u = t - INTRO - .8, ramp = .8, rate = TAU / SPIN;
        return u <= 0 ? 0 : u < ramp ? rate * u * u / (2 * ramp) : rate * (u - ramp / 2);
      }

      function shuffle(t: number) {
        const settle = sineInOut(t / INTRO);
        const push = outCubic((t - INTRO - .3) / 1);
        pose.settle = settle;
        pose.yaw = REST_YAW * settle + spinAngle(t);
        pose.pitch = TILT * settle;
        // Keep the loops inside the stage on short screens.
        const stage = anchor()?.parentElement?.getBoundingClientRect(), width = anchor()?.getBoundingClientRect().width || 1;
        const reach = LIFT + PUSH + (SHUFFLE - 1) * (GAP + RING_GAP) + .8;
        const room = stage ? Math.min(1, Math.max(.55, (stage.height / 2 + 15) / width / reach)) : 1;
        for (let j = 0; j < SHUFFLE; j++) {
          const {turn, lift} = loop(t - INTRO - (SHUFFLE - 1 - j) * STAGGER);
          const radius = j * GAP * Math.max(settle, .15) + push * room * (PUSH + j * RING_GAP);
          pose.y[j] = lift * room * LIFT + radius * Math.sin(turn);
          pose.z[j] = radius * Math.cos(turn) - centre;
        }
      }

      function placeDeck() {
        const box = anchor()?.getBoundingClientRect();
        if (!box) return;
        const at = toWorld(box.left + box.width / 2, box.top + box.height / 2, 0);
        lean.x += (lean.tx - lean.x) * .06; lean.y += (lean.ty - lean.y) * .06;
        deck.position.copy(at.p);
        deck.scale.setScalar(box.width * at.k);
        deck.rotation.set(pose.pitch + lean.x * pose.settle, pose.yaw + lean.y * pose.settle, 0);
        // Unlit art keeps its exact colours; turning side-on and depth in the stack darken it a little.
        const facing = .6 + .4 * Math.abs(Math.cos(deck.rotation.y));
        for (let j = 0; j < SHUFFLE; j++) {
          meshes[j].position.set(0, pose.y[j], pose.z[j]);
          meshes[j].rotation.z = jitter[j] * pose.settle;
          tints[j].setScalar(facing * (.8 + .2 * j / (SHUFFLE - 1)));
        }
        shadow.position.set(at.p.x, at.p.y - box.height * .6, at.p.z - 30);
        shadow.scale.set(box.width * 1.9, box.width * .34, 1);
      }

      function planSpread() {
        const fan = document.querySelector('.ritual-fan')?.getBoundingClientRect();
        const view = document.querySelector('.ritual-fan-scroll')?.getBoundingClientRect();
        const first = document.querySelector<HTMLElement>('.ritual-fan .ritual-deck-card');
        if (!fan || !view || !first) return false;
        const w = first.offsetWidth, h = first.offsetHeight, top = fan.top + 10;
        // The travelling cards become evenly spaced fan positions; the rest of the deck fills in between them,
        // starting inside the gathered stack so the deck simply grows into the full 78-card fan.
        const fanOf = new Array<number>(CARDS), used = new Set<number>();
        for (let j = 0; j < SHUFFLE; j++) {fanOf[j] = Math.round(j * (CARDS - 1) / (SHUFFLE - 1)); used.add(fanOf[j]);}
        for (let m = SHUFFLE, f = 0; m < CARDS; m++) {while (used.has(f)) f++; fanOf[m] = f++;}
        scene.updateMatrixWorld(true);
        const base = deck.quaternion.clone();
        const startPoses = meshes.map((mesh, m) => {
          if (m >= SHUFFLE) mesh.position.set(0, 0, fanOf[m] * (SHUFFLE - 1) / (CARDS - 1) * GAP - centre);
          mesh.rotation.z = jitter[m];
          mesh.visible = true;
          mesh.updateMatrixWorld(true);
          const p = new THREE.Vector3().setFromMatrixPosition(mesh.matrixWorld);
          scene.attach(mesh);
          return {p, s: deck.scale.x, tilt: jitter[m]};
        });
        const mid = meshes.map((_, m) => {const at = toWorld(view.left + view.width / 2, top + h / 2, fanOf[m] * FAN_DEPTH); return {p: at.p, s: w * at.k};});
        const end = meshes.map((_, m) => {
          // Same geometry as the DOM card: translateY(arc) rotate(r) around transform-origin 50% 130%.
          const i = fanOf[m], arc = fanArc(i), r = arc.r * Math.PI / 180;
          const at = toWorld(fan.left + i * FAN_STEP + w / 2 + .8 * h * Math.sin(r), top + 1.3 * h + arc.y - .8 * h * Math.cos(r), i * FAN_DEPTH);
          return {p: at.p, s: w * at.k, r};
        });
        // On phones the choice bar is sticky over the bottom of the fan; the DOM fan passes under it, so clip there too.
        const bar = document.querySelector('.ritual-choice-bar')?.getBoundingClientRect();
        const bottom = Math.min(innerHeight, bar && bar.top > view.top && bar.top < view.bottom ? bar.top : view.bottom);
        plan = {base, start: startPoses, mid, end, clip: [view.left, view.width, bottom], fan: {left: fan.left, top: fan.top}};
        shadow.visible = false;
        return true;
      }

      let visible = !document.hidden, onscreen = true, activeTime = 0, previousTime = -1;
      const visibility = () => {visible = !document.hidden; previousTime = -1;};
      document.addEventListener('visibilitychange', visibility);
      // One callback can carry several entries when visibility flips quickly; only the latest is current.
      const observer = new IntersectionObserver((entries) => {onscreen = entries[entries.length - 1].isIntersecting; previousTime = -1;});
      const host = anchor()?.parentElement;
      if (host) observer.observe(host);
      teardown.push(() => {observer.disconnect(); document.removeEventListener('visibilitychange', visibility);});
      function frame(rawTime: number) {
        // Only the idle shuffle can sleep offscreen; a transition must always finish.
        if (!visible || (!onscreen && phaseRef.current === 'shuffling')) {previousTime = -1; return;}
        if (previousTime >= 0) activeTime += Math.max(0, rawTime - previousTime);
        previousTime = rawTime;
        const time = activeTime;
        if (mode === 'done') return;
        const dt = last < 0 ? 0 : Math.min(time - last, .1);
        last = time;
        const wanted = phaseRef.current;
        if (wanted !== 'shuffling' && mode === 'shuffle') {
          // Gather from wherever the deck is; the deck finishes its turn forward to the resting angle.
          mode = 'gather'; start = time;
          from.y.set(pose.y); from.z.set(pose.z); from.yaw = pose.yaw; from.pitch = pose.pitch;
          from.spin = clock > INTRO + .8 ? TAU / SPIN : 0;
          const ahead = ((REST_YAW - pose.yaw) % TAU + TAU) % TAU;
          from.yawTo = pose.yaw + ahead;
          from.yawTime = Math.min(1.5, Math.max(.6, ahead / Math.max(from.spin, .5) * 1.3));
        }
        if (wanted === 'spreading' && (mode === 'held' || mode === 'gather')) {
          if (!planSpread()) {mode = 'done'; calls.current.onSpread(); return;}
          mode = 'spread'; start = time;
        }
        if (mode === 'shuffle') {
          clock += dt;
          shuffle(clock);
          placeDeck();
        } else if (mode === 'gather') {
          const k = Math.min((time - start) / GATHER, 1), e = inOut(k);
          // Cubic Hermite: leaves at the current turning speed and arrives at rest without a jolt.
          const u = Math.min((time - start) / from.yawTime, 1), span = from.yawTo - from.yaw;
          pose.yaw = from.yaw + from.spin * from.yawTime * (u - 2 * u * u + u * u * u) + span * (3 * u * u - 2 * u * u * u);
          pose.pitch = from.pitch + (TILT - from.pitch) * e;
          pose.settle = 1;
          for (let j = 0; j < SHUFFLE; j++) {pose.y[j] = from.y[j] * (1 - e); pose.z[j] = from.z[j] + (j * GAP - centre - from.z[j]) * e;}
          placeDeck();
          if (k >= 1 && u >= 1) {mode = 'held'; calls.current.onGathered();}
        } else if (mode === 'held') {
          placeDeck();
        } else if (mode === 'spread' && plan) {
          const k = Math.min((time - start) / SPREAD, 1), split = .42;
          const first = k < split, e = first ? inOut(k / split) : outQuart((k - split) / (1 - split));
          // Follow the fan if the page or the fan scrolls while the cards are in the air.
          const now = document.querySelector('.ritual-fan')?.getBoundingClientRect();
          const follow = first ? e : 1, dx = now ? (now.left - plan.fan.left) * follow : 0, dy = now ? (now.top - plan.fan.top) * follow : 0;
          // All cards share one orientation (only their in-plane tilt differs), so they stay parallel in flight.
          if (first) baseQ.slerpQuaternions(plan.base, identity, e); else baseQ.copy(identity);
          meshes.forEach((mesh, m) => {
            const a = first ? plan!.start[m] : plan!.mid[m], b = first ? plan!.mid[m] : plan!.end[m];
            mesh.position.lerpVectors(a.p, b.p, e);
            mesh.position.x += dx; mesh.position.y -= dy;
            const s = a.s + (b.s - a.s) * e;
            mesh.scale.set(s, s, s * (first ? 1 - .7 * e : .3));
            const tilt = first ? plan!.start[m].tilt * (1 - e) : -plan!.end[m].r * e;
            mesh.quaternion.copy(baseQ).multiply(turnQ.setFromAxisAngle(zAxis, tilt));
            if (first) tints[m].lerp(white, .15); else tints[m].copy(white);
          });
          // The DOM fan scrolls inside its own box; clip the flying cards to the same box (scissor y is from the bottom).
          renderer.setScissorTest(true);
          renderer.setScissor(plan.clip[0], innerHeight - plan.clip[2], plan.clip[1], plan.clip[2]);
          if (k >= 1) {
            // The DOM fan now appears underneath at the same pixels; fade the canvas out over it, then let go.
            renderer.render(scene, camera); mode = 'done'; calls.current.onSpread();
            canvas.style.transition = 'opacity .2s linear';
            requestAnimationFrame(() => {canvas.style.opacity = '0';});
            const timer = setTimeout(release, 260);
            teardown.push(() => clearTimeout(timer));
            return;
          }
        }
        renderer.render(scene, camera);
        const host = anchor();
        if (host) host.dataset.pose = pose.yaw.toFixed(4) + ' ' + pose.y[SHUFFLE - 1].toFixed(4) + ' ' + pose.z[8].toFixed(4);
      }

      new THREE.TextureLoader().load('/cards/card-back.webp', map => {
        if (disposed) {map.dispose(); return;}
        map.colorSpace = THREE.SRGBColorSpace;
        map.anisotropy = renderer.capabilities.getMaxAnisotropy();
        const faces: Three.Material[] = [];
        for (let m = 0; m < CARDS; m++) {
          const face = new THREE.MeshBasicMaterial({map, alphaTest: .5});
          faces.push(face); tints.push(face.color);
          const mesh = new THREE.Mesh(geometry, [face, edge]);
          // Only the travelling cards are drawn during the shuffle; the rest wait inside the stack.
          mesh.visible = m < SHUFFLE;
          deck.add(mesh); meshes.push(mesh);
        }
        teardown.push(() => {map.dispose(); faces.forEach(f => f.dispose());});
        document.body.append(canvas);
        live = true;
        anchor()?.classList.add('is-3d-live');
        teardown.push(() => anchor()?.classList.remove('is-3d-live'));
        // Drive frames from the GSAP ticker when present, so pausing GSAP pauses the deck as well.
        if (motion) {
          const tick = (time: number) => frame(time);
          motion.ticker.add(tick);
          teardown.push(() => motion.ticker.remove(tick));
        } else {
          let raf = 0;
          const loopFrame = (ms: number) => {frame(ms / 1000); raf = requestAnimationFrame(loopFrame);};
          raf = requestAnimationFrame(loopFrame);
          teardown.push(() => cancelAnimationFrame(raf));
        }
      }, undefined, fail);
    }).catch(fail);
    return () => {disposed = true; release();};
  },[]);
  return null;
}

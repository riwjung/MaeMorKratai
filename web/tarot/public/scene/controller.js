(() => {
  'use strict';

  // This bridge belongs to the interactive website. The exported HyperFrames
  // composition keeps its original finite timeline in index.html.
  const master = window.__timelines?.['maemorkratai-halloween'];
  const valid = new Set(['the-fool', 'three-of-wands', 'the-lovers', 'the-hanged-man', 'queen-of-swords']);
  const ns = 'http://www.w3.org/2000/svg';
  const preference = matchMedia('(prefers-reduced-motion: reduce)');
  const showCard = document.querySelector('#show-card');
  const front = document.querySelector('#card-front');
  const back = document.querySelector('#card-back');
  const send = (type, extra = {}) => parent.postMessage({ type, ...extra }, location.origin);
  const portrait = new URLSearchParams(location.search).get('presentation') === 'portrait';
  let portraitPlaying = false;
  if (portrait) {
    document.documentElement.style.cssText = 'width:100%;height:100%;overflow:hidden';
    document.body.style.cssText = 'width:100%;height:100%;overflow:hidden';
    document.querySelector('#halloween').style.transform = 'translate(-40px,-320px)';
    // Keep the original textured character; avoid re-rasterizing full-room turbulence
    // on every ghost/candle frame in a small portrait. Home presentation is unchanged.
    document.querySelector('#room [filter="url(#room-paper)"]')?.removeAttribute('filter');
  }
  let idle = null;
  let idleRest = [];
  let busy = false;
  let loading = false;
  let active = null;
  let reported = false;
  let requestedReducedMotion = false;
  let initialized = false;

  if (!master || !window.gsap || !showCard || !front || !back) {
    send('mmkt:error', { message: 'เตรียมฉากแม่หมอไม่สำเร็จ กรุณาโหลดหน้าใหม่' });
    return;
  }

  document.querySelector('.scene-content').style.opacity = '0';
  // The parent overlay uses this exact asset, so the card stays consistent
  // while it flips back and returns to the mascot's paw.
  const backArt = document.createElementNS(ns, 'image');
  backArt.setAttribute('href', new URL('../cards/card-back.svg', location.href).href);
  backArt.setAttribute('x', '-66');
  backArt.setAttribute('y', '-100');
  backArt.setAttribute('width', '132');
  backArt.setAttribute('height', '200');
  backArt.setAttribute('preserveAspectRatio', 'xMidYMid meet');
  back.replaceChildren(backArt);

  function anchor() {
    // Coordinates are in this iframe's viewport, before any parent CSS scale.
    const rect = showCard.getBoundingClientRect();
    return { x: rect.x, y: rect.y, width: rect.width, height: rect.height };
  }

  function stopIdle() {
    idle?.kill();
    idle = null;
    for (const [element, values] of idleRest) gsap.set(element, values);
    idleRest = [];
    gsap.set('#blink', { opacity: 0 });
  }

  function breathe() {
    stopIdle();
    if (preference.matches || requestedReducedMotion || busy || (portrait && (!portraitPlaying || document.hidden))) return;
    // Restore these exact values on interruption; repeated preference changes
    // must not gradually move the ghost or rabbit away from its original pose.
    for (const [selector, properties] of [
      ['#rabbit', ['y']],
      ['#ghost-0, #ghost-1', ['x', 'y']],
      ['.candle-glow', ['opacity']],
    ]) {
      for (const element of document.querySelectorAll(selector)) {
        idleRest.push([element, Object.fromEntries(properties.map((property) => [property, gsap.getProperty(element, property)]))]);
      }
    }
    idle = gsap.timeline({ repeat: -1 });
    // Hold the raised card still so its anchor remains stable during the
    // transfer to the parent overlay. Blinks and room details stay alive.
    if (!active) idle.to('#rabbit', { y: '-=6', duration: 2, repeat: 1, yoyo: true, ease: 'sine.inOut' }, 0);
    idle.to('#ghost-0', { y: '-=20', x: '+=8', duration: 2, repeat: 1, yoyo: true, ease: 'sine.inOut' }, 0);
    idle.to('#ghost-1', { y: '+=15', x: '-=10', duration: 2, repeat: 1, yoyo: true, ease: 'sine.inOut' }, 0);
    idle.to('.candle-glow', { opacity: 0.55, duration: 0.5, repeat: 7, yoyo: true, ease: 'sine.inOut' }, 0);
    idle.to('#blink', { opacity: 1, duration: 0.045 }, 1.4)
      .to('#blink', { opacity: 0, duration: 0.065 }, 1.55);
  }

  function resetScene() {
    stopIdle();
    master.pause(0, true);
    gsap.set(showCard, { visibility: 'visible', opacity: 0, x: 0, y: 0, rotation: 0 });
    gsap.set('#card-flip', { scaleX: 1 });
    gsap.set('#card-back', { opacity: 1 });
    gsap.set(front, { opacity: 0 });
  }

  function setCardFace(frontVisible) {
    gsap.set(showCard, { opacity: 1, visibility: 'visible' });
    gsap.set('#card-flip', { scaleX: 1 });
    gsap.set('#card-back', { opacity: frontVisible ? 0 : 1 });
    gsap.set(front, { opacity: frontVisible ? 1 : 0 });
  }

  function finishReveal() {
    if (!busy || loading || reported || !active) return;
    reported = true;
    busy = false; // Set before seeking, because GSAP can invoke onUpdate.
    master.pause(7.15, true);
    setCardFace(true);
    breathe();
    send('mmkt:revealed', { cardId: active, anchor: anchor() });
  }

  async function loadArt(url) {
    const image = new Image();
    image.src = url;
    let timeout;
    try {
      await Promise.race([
        image.decode(),
        new Promise((_, reject) => {
          timeout = setTimeout(() => reject(new Error('Card image timed out')), 10000);
        }),
      ]);
    } finally {
      clearTimeout(timeout);
    }
  }

  async function draw(data) {
    if (busy || !valid.has(data.cardId)) return;
    busy = true;
    loading = true;
    active = data.cardId;
    reported = false;
    requestedReducedMotion = data.reducedMotion === true;
    resetScene();
    const url = new URL('../cards/' + active + '.jpeg', location.href).href;
    try {
      await loadArt(url);
      const art = document.createElementNS(ns, 'image');
      art.setAttribute('href', url);
      art.setAttribute('x', '-66');
      art.setAttribute('y', '-100');
      art.setAttribute('width', '132');
      art.setAttribute('height', '200');
      art.setAttribute('preserveAspectRatio', 'xMidYMid meet');
      front.replaceChildren(art);
      loading = false;
      if (preference.matches || requestedReducedMotion) finishReveal();
      else master.restart();
    } catch {
      const cardId = active;
      loading = false;
      busy = false;
      active = null;
      reported = false;
      requestedReducedMotion = false;
      resetScene();
      breathe();
      send('mmkt:error', { cardId, message: 'โหลดหน้าไพ่ไม่สำเร็จ ลองอีกครั้งได้เลย' });
    }
  }

  window.addEventListener('message', (event) => {
    if (event.source !== parent || event.origin !== location.origin || !event.data) return;
    const data = event.data;
    switch (data.type) {
      case 'mmkt:hello':
        if (initialized) send('mmkt:ready');
        break;
      case 'mmkt:portrait-motion':
        if (portrait && typeof data.playing === 'boolean') {
          portraitPlaying = data.playing;
          if (portraitPlaying) breathe(); else stopIdle();
        }
        break;
      case 'mmkt:draw':
        if (initialized && !portrait) void draw(data);
        break;
      case 'mmkt:card-visibility':
        if (!busy && active && typeof data.visible === 'boolean') {
          if (data.visible) breathe(); else stopIdle();
          gsap.set(showCard, { visibility: data.visible ? 'visible' : 'hidden' });
        }
        break;
      case 'mmkt:stow':
        if (!busy && active && data.cardId === active) {
          setCardFace(false);
          breathe();
          send('mmkt:stowed', { cardId: active, anchor: anchor() });
        }
        break;
      case 'mmkt:show':
        if (!busy && active && data.cardId === active) {
          setCardFace(true);
          send('mmkt:revealed', { cardId: active, anchor: anchor() });
        }
        break;
      case 'mmkt:anchor':
        if (!busy && active) send('mmkt:anchor', { cardId: active, anchor: anchor() });
        break;
    }
  });

  preference.addEventListener('change', () => {
    if (preference.matches) {
      stopIdle();
      // If decoding is still pending, draw() observes the updated preference
      // when it completes. Otherwise reveal immediately and release busy.
      if (busy && !loading) finishReveal();
    } else if (!busy) breathe();
  });

  master.eventCallback('onUpdate', () => {
    if (busy && !loading && !reported && master.time() >= 7.12) finishReveal();
  });
  master.eventCallback('onComplete', () => {
    if (busy && !loading) finishReveal();
  });

  if (portrait) document.addEventListener('visibilitychange', () => {
    if (document.hidden) stopIdle(); else breathe();
  });
  if (portrait) window.addEventListener('pagehide', () => {stopIdle(); master.pause();});
  resetScene();
  breathe();
  initialized = true;
  send('mmkt:ready');
})();

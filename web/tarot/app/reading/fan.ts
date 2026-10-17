// Shared fan geometry: the DOM fan (CSS vars) and the WebGL spread both land cards here.
export const FAN_STEP = 28;
export const fanArc = (i: number) => {const t = (i - 38.5) / 38.5; return {y: t * t * 40, r: t * 13};};

import catalog from './reading-cards.json';

export const cards = catalog;
export type Card = typeof cards[number];
export const contexts = ['คนโสด', 'แอบชอบ', 'คุยกัน', 'ซับซ้อน', 'มีแฟน', 'เลิกกัน'] as const;
export type LoveContext = typeof contexts[number];
export type Category = 'love' | 'work' | 'money' | 'life';
export const categories: {id: Category; label: string; icon: string; hint: string}[] = [
  {id: 'love', label: 'ความรัก', icon: '♡', hint: 'ความรู้สึกและความสัมพันธ์'},
  {id: 'work', label: 'การงาน', icon: '✧', hint: 'เส้นทางที่กำลังเติบโต'},
  {id: 'money', label: 'การเงิน', icon: '☾', hint: 'ความมั่นคงและการวางแผน'},
  {id: 'life', label: 'ภาพรวมชีวิต', icon: '✺', hint: 'กลับมาฟังเสียงข้างใน'},
];
export const situations: Record<Category, readonly string[]> = {
  love: contexts,
  work: ['งานปัจจุบัน', 'มองหางานใหม่', 'ธุรกิจของตัวเอง'],
  money: ['รายรับและรายจ่าย', 'วางแผนเก็บเงิน', 'เป้าหมายระยะยาว'],
  life: ['กำลังเปลี่ยนแปลง', 'มีเรื่องต้องตัดสินใจ', 'อยากทบทวนตัวเอง'],
};
export const suggestions: Record<Category, readonly string[]> = {
  love: ['ความสัมพันธ์นี้กำลังพาฉันไปทางไหน?', 'มีอะไรในใจที่ฉันควรทำความเข้าใจ?', 'ฉันควรดูแลหัวใจตัวเองอย่างไร?'],
  work: ['ฉันอยากเห็นอะไรเปลี่ยนไปในเส้นทางการทำงาน?', 'อะไรทำให้ฉันรู้สึกติดขัดกับงานตอนนี้?', 'ฉันอยากเติบโตในทิศทางไหน?'],
  money: ['ฉันอยากปรับนิสัยการใช้เงินเรื่องไหน?', 'ความมั่นคงมีความหมายอย่างไรสำหรับฉัน?', 'เป้าหมายทางการเงินที่สำคัญตอนนี้คืออะไร?'],
  life: ['ช่วงนี้ฉันควรกลับมาฟังตัวเองเรื่องอะไร?', 'มีอะไรที่ฉันพร้อมจะปล่อยวาง?', 'ฉันอยากให้ชีวิตค่อย ๆ เปลี่ยนไปอย่างไร?'],
};
export const positions = ['อดีต', 'ปัจจุบัน', 'อนาคต'] as const;
export type ReadingRequest = {category: Category; situation: string; question: string; spread: 'past-present-future'};
export type Phase = 'topic' | 'question' | 'shuffling' | 'gathering' | 'spreading' | 'selecting' | 'revealing' | 'locked' | 'reading';
// slots follow the spread positions (past, present, future); a card keeps the slot it was placed in.
export type DrawSession = {phase: Phase; deck: string[]; slots: (string | null)[]; opened: boolean[]; unlocked: boolean};
export const initialSession: DrawSession = {phase: 'topic', deck: [], slots: [null, null, null], opened: [false, false, false], unlocked: false};
export type Action = {type: 'QUESTION' | 'TOPIC' | 'EDIT' | 'STOP' | 'GATHERED' | 'SPREAD' | 'REVEAL' | 'NEXT_REVEAL' | 'UNLOCK' | 'RESET'} | {type: 'START'; deck: string[]} | {type: 'PICK'; id: string; slot?: number} | {type: 'REMOVE'; id: string} | {type: 'OPEN'; slot: number};
export const placedCards = (s: DrawSession) => s.slots.filter((id): id is string => id !== null);
const openSlot = (s: DrawSession, slot: number) => s.opened.map((open, i) => open || i === slot);
export function sessionReducer(s: DrawSession, action: Action): DrawSession {
  switch (action.type) {
    case 'QUESTION': return s.phase === 'topic' ? {...s, phase: 'question'} : s;
    case 'TOPIC': return s.phase === 'question' ? {...s, phase: 'topic'} : s;
    case 'EDIT': return ['shuffling','selecting'].includes(s.phase) ? {...initialSession, phase: 'question'} : s;
    case 'START': return s.phase === 'question' && action.deck.length === 78 && new Set(action.deck).size === 78 && action.deck.every(id => cards.some(c => c.id === id)) ? {...initialSession, phase: 'shuffling', deck: action.deck} : s;
    case 'STOP': return s.phase === 'shuffling' ? {...s, phase: 'gathering'} : s;
    case 'GATHERED': return s.phase === 'gathering' ? {...s, phase: 'spreading'} : s;
    case 'SPREAD': return s.phase === 'spreading' ? {...s, phase: 'selecting'} : s;
    case 'PICK': {
      // Without a slot the card takes the first empty one; a named slot must be empty.
      const slot = action.slot ?? s.slots.indexOf(null);
      if (s.phase !== 'selecting' || !s.deck.includes(action.id) || s.slots.includes(action.id) || slot < 0 || slot > 2 || s.slots[slot] !== null) return s;
      return {...s, slots: s.slots.map((id, i) => i === slot ? action.id : id)};
    }
    case 'REMOVE': {
      // An opened card has been seen and stays; removing leaves its slot empty instead of shifting the others.
      const slot = s.slots.indexOf(action.id);
      return s.phase === 'selecting' && slot >= 0 && !s.opened[slot] ? {...s, slots: s.slots.map((id, i) => i === slot ? null : id)} : s;
    }
    case 'OPEN': {
      if (s.phase !== 'selecting' || !s.slots[action.slot] || s.opened[action.slot]) return s;
      const opened = openSlot(s, action.slot);
      return {...s, opened, phase: opened.every(Boolean) ? 'locked' : 'selecting'};
    }
    case 'REVEAL': return s.phase === 'selecting' && s.slots.every(id => id !== null) ? {...s, phase: 'revealing'} : s;
    case 'NEXT_REVEAL': {
      if (s.phase !== 'revealing') return s;
      const opened = openSlot(s, s.opened.indexOf(false));
      return {...s, opened, phase: opened.every(Boolean) ? 'locked' : 'revealing'};
    }
    case 'UNLOCK': return s.phase === 'locked' ? {...s, phase: 'reading', unlocked: true} : s;
    case 'RESET': return initialSession;
  }
}
export function randomBelow(n: number): number {
  const ceiling = Math.floor(0x100000000 / n) * n;
  const buffer = new Uint32Array(1);
  do { crypto.getRandomValues(buffer); } while (buffer[0] >= ceiling);
  return buffer[0] % n;
}
export function shuffleDeck(): string[] {
  const deck = cards.map(c => c.id);
  for (let i = deck.length - 1; i > 0; i--) {
    const j = randomBelow(i + 1);
    [deck[i], deck[j]] = [deck[j], deck[i]];
  }
  return deck;
}
export type ReadingResult = {
  status: 'demo'; knowledgeVersion: string; request: ReadingRequest;
  entries: {id: string; name: string; position: string; text: string; source: {url: string; message: number; line: number} | null}[];
  summary: string; reflection: string;
};
export function createReading(request: ReadingRequest, selected: string[]): ReadingResult {
  if (selected.length !== 3 || new Set(selected).size !== 3) throw new Error('ต้องเลือกไพ่ต่างกันครบ 3 ใบ');
  if (!situations[request.category].includes(request.situation)) throw new Error('สถานการณ์ไม่ตรงกับหมวดคำถาม');
  const entries = selected.map((id, i) => {
    const card = cards.find(c => c.id === id);
    if (!card) throw new Error('ไม่พบไพ่');
    return {id, name: card.name, position: positions[i],
      text: request.category === 'love' ? card.meanings[request.situation as LoveContext] : `ไพ่ ${card.name} อยู่ในตำแหน่ง${positions[i]} สำหรับหัวข้อ “${request.situation}” — ส่วนนี้รอคำอ่านจากแม่หมอกระต่าย`,
      source: request.category === 'love' ? {url: card.source_url, message: card.source_message, line: card.source_line} : null};
  });
  const summary = request.category === 'love'
    ? `ในบริบท “${request.situation}” ลองวางทั้งสามมุมไว้ข้างกัน: อดีต · ${entries[0].name} — ${entries[0].text} / ปัจจุบัน · ${entries[1].name} — ${entries[1].text} / อนาคต · ${entries[2].name} — ${entries[2].text} การเชื่อมความหมายตามเวลาและความสัมพันธ์ระหว่างไพ่ยังรอเจ้าของทบทวน จึงยังไม่ใช่บทสรุปคำทำนายที่ผ่านการรับรอง`
    : `สำหรับ “${categories.find(c => c.id === request.category)!.label} · ${request.situation}” คุณเลือก ${entries.map(e => `${e.name} (${e.position})`).join(' → ')} ไว้แล้ว บทสรุปเฉพาะหมวดนี้จะพร้อมเมื่อแม่หมอกระต่ายเพิ่มและทบทวนความรู้`;
  return {status: 'demo', knowledgeVersion: 'love-2026-10-15-unreviewed.demo-1', request, entries, summary,
    reflection: request.category === 'love' ? 'เมื่อมองทั้งสามใบ มีความรู้สึกใดที่ตรงกับคุณ และมีอะไรที่อยากพูดคุยให้ชัดเจนขึ้น?' : `เมื่อคิดถึง “${request.situation}” มีสิ่งเล็ก ๆ อะไรที่คุณอยากเริ่มทบทวนด้วยตัวเอง?`};
}

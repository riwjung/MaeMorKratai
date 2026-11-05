import dailyCards from '../lib/daily-cards.json';

export type DailyCard = typeof dailyCards.cards[number];

export const contexts = ['คนโสด', 'คนแอบชอบ', 'คนคุย', 'ความสัมพันธ์ซับซ้อน', 'คนมีแฟน', 'คนรักเก่า'] as const;
export type Context = typeof contexts[number];

const loveKeys: Record<Context, keyof DailyCard['content']['love_by_status']> = {
  'คนโสด': 'single',
  'คนแอบชอบ': 'crush',
  'คนคุย': 'talking',
  'ความสัมพันธ์ซับซ้อน': 'complicated',
  'คนมีแฟน': 'partnered',
  'คนรักเก่า': 'ex_partner',
};

const dailyById = new Map(dailyCards.cards.map(card => [card.card_id, card]));

export function getDailyCard(id: string): DailyCard {
  const card = dailyById.get(id);
  if (!card) throw new Error(`Missing daily reading: ${id}`);
  return card;
}

export function getLoveReading(card: DailyCard, context: Context): string | null {
  return card.content.love_by_status[loveKeys[context]];
}

function SourceText({text}: {text: string}) {
  return <>{text.split(/(\*\*[^*]+\*\*)/g).map((part, index) => part.startsWith('**') && part.endsWith('**')
    ? <strong key={index}>{part.slice(2, -2)}</strong> : part)}</>;
}

export function DailyReading({card, context, allLove = false}: {card: DailyCard; context: Context; allLove?: boolean}) {
  const content = card.content;
  const love = getLoveReading(card, context);
  return <div className="daily-reading">
    <section><h3>ภาพรวมวันนี้</h3><p><SourceText text={content.overview}/></p></section>
    <section><h3>การงาน</h3><p><SourceText text={content.work}/></p></section>
    <section><h3>การเงิน</h3><p><SourceText text={content.money}/></p></section>
    <section><h3>ความรัก · {context}</h3><p><SourceText text={love ?? 'แชทต้นทางยังไม่มีคำอ่านสำหรับสถานะนี้ของไพ่ใบนี้'}/></p></section>
    <section><h3>ข้อความจากแม่หมอ</h3><p><SourceText text={content.rabbit_message}/></p></section>
    <div className="daily-extras"><p><strong>สีประจำวัน</strong> {content.colors}</p><p><strong>คำยืนยันกับตัวเอง</strong> {content.affirmation}</p></div>
    {allLove && <div className="reading-full"><h3>ความรักในสถานะอื่น</h3><dl>{contexts.filter(label => label !== context).map(label => <div key={label}><dt>{label}</dt><dd>{getLoveReading(card, label) ?? 'ยังไม่มีคำอ่านในแชทต้นทาง'}</dd></div>)}</dl></div>}
  </div>;
}

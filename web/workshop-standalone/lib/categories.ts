// Labels only. Scenario text and unrevealed cards stay in the server bundle.
export const categories = [
  {id:'love',label:'ความรัก'},
  {id:'work',label:'การงาน'},
  {id:'money',label:'การเงิน'},
  {id:'health',label:'สุขภาพ'},
] as const;
export const categoryLabel=(id:string)=>categories.find(c=>c.id===id)?.label||'ทุกหมวด';

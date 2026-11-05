import manifest from '../public/cards/v3/manifest.json';

type CardArt = {id:string;art?:string|null};
export function cardArtSize(card:CardArt) {
 const art=manifest.cards.find(item=>item.id===card.id&&item.art===card.art);
 return art?{...art,width:art.renderedWidth,height:art.renderedHeight}:undefined;
}
export function cardAspectRatio(card:CardArt) {
 const art=cardArtSize(card);
 return art?`${art.width} / ${art.height}`:'1632 / 2624';
}

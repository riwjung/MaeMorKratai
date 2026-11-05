'use client';
import {useState} from 'react';
import {cardArtSize,cardAspectRatio} from '../lib/card-art';

export default function CardFace({card,className='',lazy=false}:{card:{id:string;name:string;art?:string|null};className?:string;lazy?:boolean}) {
 const [failed,setFailed]=useState<string|null>(null);
 const size=cardArtSize(card),style={aspectRatio:cardAspectRatio(card)};
 if(card.art&&failed!==card.art)return <img className={className} style={style} width={size?.width} height={size?.height} src={card.art} alt={'ไพ่ '+card.name} draggable={false} loading={lazy?'lazy':'eager'} onError={()=>setFailed(card.art!)}/>;
 return <div className={'card-name-fallback '+className} style={style} role="img" aria-label={'ไพ่ '+card.name}><span>{card.name}</span></div>;
}

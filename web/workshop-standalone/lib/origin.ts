// Next may normalize request.url to localhost behind its proxy. The Host header
// retains the actual requested authority; never accept an unrelated Origin.
export function sameOrigin(request:Request):boolean {
 const origin=request.headers.get('origin'),host=request.headers.get('host');
 if(!origin||!host)return false;
 try{
  const parsed=new URL(origin);
  return parsed.origin===origin&&parsed.host===host.toLowerCase()&&
   (parsed.protocol==='https:'||
    (parsed.protocol==='http:'&&['localhost','127.0.0.1','[::1]'].includes(parsed.hostname)));
 }catch{return false}
}

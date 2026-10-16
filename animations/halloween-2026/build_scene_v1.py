from pathlib import Path
import json

P = Path(__file__).resolve().parent
DURATION = 12
defs = '''<defs>
<radialGradient id="wall"><stop stop-color="#714575"/><stop offset=".68" stop-color="#45254f"/><stop offset="1" stop-color="#21132e"/></radialGradient>
<linearGradient id="wood" x2="0" y2="1"><stop stop-color="#6a3a5d"/><stop offset=".5" stop-color="#41223e"/><stop offset="1" stop-color="#221527"/></linearGradient>
<linearGradient id="night" x2="0" y2="1"><stop stop-color="#211432"/><stop offset="1" stop-color="#6a447e"/></linearGradient>
<radialGradient id="warm"><stop stop-color="#ffd495" stop-opacity=".65"/><stop offset=".4" stop-color="#ee905c" stop-opacity=".2"/><stop offset="1" stop-color="#df884e" stop-opacity="0"/></radialGradient>
<radialGradient id="mist"><stop stop-color="#c29bd5" stop-opacity=".23"/><stop offset="1" stop-color="#c29bd5" stop-opacity="0"/></radialGradient>
<linearGradient id="ghostFill" x2=".7" y2="1"><stop stop-color="#fff9ec"/><stop offset=".55" stop-color="#eaddef"/><stop offset="1" stop-color="#be9dcc"/></linearGradient>
<linearGradient id="pot" x2="1" y2="1"><stop stop-color="#71476a"/><stop offset=".3" stop-color="#352037"/><stop offset="1" stop-color="#170f22"/></linearGradient>
<linearGradient id="flame" x2="0" y2="1"><stop stop-color="#fff8d3"/><stop offset=".6" stop-color="#ffd28b"/><stop offset="1" stop-color="#ed8e56"/></linearGradient>
<filter id="soft"><feGaussianBlur stdDeviation="5"/></filter>
<filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="8" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="paper"><feTurbulence type="fractalNoise" baseFrequency=".53" numOctaves="3" seed="24"/><feColorMatrix type="saturate" values="0"/><feComponentTransfer><feFuncA type="linear" slope=".12"/></feComponentTransfer><feBlend in="SourceGraphic" mode="soft-light"/></filter>
<filter id="shadow"><feDropShadow dx="0" dy="12" stdDeviation="18" flood-color="#110a1b" flood-opacity=".65"/></filter>
<g id="star"><path d="M0 -12 Q2 -2 9 0 Q2 2 0 12 Q-2 2 -9 0 Q-2 -2 0 -12" fill="#ffdfaa"/></g>
<g id="card"><rect width="90" height="140" rx="9" fill="#f2d8b9" stroke="#b47d70" stroke-width="3"/><rect x="7" y="7" width="76" height="126" rx="5" fill="#4a285b" stroke="#d9ad79" stroke-width="2"/><path d="M45 24 L70 70 45 116 20 70 Z" fill="none" stroke="#cda17c" stroke-width="1.6"/><circle cx="45" cy="70" r="20" fill="none" stroke="#e7c290" stroke-width="2"/><path d="M48 54 A17 17 0 1 0 48 86 A14 14 0 0 1 48 54" fill="#f2d4a5"/><circle cx="25" cy="24" r="2" fill="#e7c290"/><circle cx="65" cy="116" r="2" fill="#e7c290"/></g>
<g id="ghost"><path d="M-62 23 C-72 -30 -45 -80 0 -80 C45 -80 65 -43 62 9 Q60 40 89 59 Q65 65 42 51 Q30 78 6 58 Q-11 83 -33 61 Q-58 81 -79 66 Q-56 47 -62 23Z" fill="url(#ghostFill)" stroke="#d7bce0" stroke-width="2"/><path d="M-57 -26 Q-49 -63 -16 -68" fill="none" stroke="#fffaf0" stroke-width="5" stroke-linecap="round" opacity=".65"/><ellipse cx="-20" cy="-13" rx="6" ry="9" fill="#5e4264"/><ellipse cx="20" cy="-13" rx="6" ry="9" fill="#5e4264"/><path d="M-8 8 Q0 16 8 8" fill="none" stroke="#765775" stroke-width="3" stroke-linecap="round"/><ellipse cx="-33" cy="4" rx="10" ry="5" fill="#e9a9bd" opacity=".65"/><ellipse cx="33" cy="4" rx="10" ry="5" fill="#e9a9bd" opacity=".65"/></g>
</defs>'''

def bottle(x,y,color,scale=1,shape=0):
    return f'''<g transform="translate({x} {y}) scale({scale})"><path d="M-14 -92 L14 -92 14 -58 Q49 -35 40 0 Q0 14 -40 0 Q-49 -35 -14 -58Z" fill="{color}" fill-opacity=".55" stroke="#c39abe" stroke-width="2"/><path d="M-38 -22 Q0 -8 38 -22 L37 -2 Q0 10 -37 -2Z" fill="{color}" opacity=".7"/><rect x="-17" y="-102" width="34" height="16" rx="4" fill="#986a68" stroke="#d3a57f" stroke-width="2"/><path d="M-20 -50 Q-32 -35 -30 -15" stroke="#f4d7ed" stroke-width="5" opacity=".38" fill="none" stroke-linecap="round"/><rect x="-18" y="-32" width="36" height="27" rx="5" fill="#dfc2b0"/><path d="M0 -27 L8 -18 0 -9 -8 -18Z" fill="none" stroke="#805076" stroke-width="2"/></g>'''

room = '''<rect width="1080" height="1920" fill="url(#wall)"/>
<path d="M0 0L190 90 190 1310 0 1560Z" fill="#25192f" opacity=".65"/><path d="M1080 0L890 90 890 1310 1080 1560Z" fill="#25192f" opacity=".65"/>
<path d="M0 1440 L190 1270 890 1270 1080 1440 1080 1920 0 1920Z" fill="#261629"/>
<path d="M190 1270L65 1920 M400 1270L360 1920 M680 1270L720 1920 M890 1270L1015 1920 M0 1490H1080 M0 1690H1080" stroke="#68405c" opacity=".22" stroke-width="4"/>
<path d="M-30 180 Q540 -150 1110 180" fill="none" stroke="#1c102c" stroke-width="50"/>
<path d="M-30 172 Q540 -148 1110 172" fill="none" stroke="#91618b" stroke-width="6" opacity=".5"/>
<path d="M318 760 L318 390 A222 222 0 0 1 762 390 L762 760Z" fill="url(#night)" stroke="#271730" stroke-width="34"/>
<path d="M318 760 L318 390 A222 222 0 0 1 762 390 L762 760Z" fill="none" stroke="#ab7793" stroke-width="5"/>
<circle cx="636" cy="337" r="155" fill="url(#warm)"/>
<path d="M659 238 A97 97 0 1 0 693 419 A92 92 0 0 1 659 238" fill="#ffe0ad" filter="url(#glow)"/>
<path d="M540 172V765 M320 475H760" stroke="#3a2545" stroke-width="16"/>
<path d="M307 764H773" stroke="#9b6489" stroke-width="18" stroke-linecap="round"/>
<path d="M35 235 Q149 190 266 245 L266 910 35 910Z" fill="#22182d" stroke="#8a5b7d" stroke-width="6"/>
<path d="M814 245 Q929 190 1045 235 L1045 910 814 910Z" fill="#22182d" stroke="#8a5b7d" stroke-width="6"/>
'''
for x in (45,824):
    for y in (440,650,885):
        room+=f'<rect x="{x-9}" y="{y}" width="241" height="19" rx="5" fill="url(#wood)" stroke="#ae778d" stroke-width="2"/>'
for x,y,c,s in [(90,432,'#b780ce',.76),(168,432,'#f3ac70',.9),(238,432,'#9774bd',.48),(86,642,'#e6a072',.6),(173,642,'#9f76be',1),(235,642,'#d18ab1',.5),(873,432,'#d8906a',.72),(958,432,'#b68fca',.9),(1020,432,'#ebba89',.4),(864,642,'#af80c5',.64),(944,642,'#ee9e60',1),(1020,642,'#a375c7',.5)]:room+=bottle(x,y,c,s)
for x in (62,103,138,190,838,880,929,975):
    h=95+(x%4)*22
    room+=f'<g transform="rotate({(x%3-1)*5} {x+15} 880)"><rect x="{x}" y="{880-h}" width="30" height="{h}" rx="3" fill="{["#70415f","#87604f","#4a375b"][x%3]}" stroke="#ba8391" stroke-width="2"/><path d="M{x+5} {898-h}H{x+25} M{x+5} 860H{x+25}" stroke="#d8ad83" stroke-width="3"/></g>'
for i in range(42):
    x=300+(i*73)%480;y=190+(i*53)%520
    room+=f'<circle cx="{x}" cy="{y}" r="{1+i%2}" fill="#f7dbb6" opacity="{.2+(i%5)*.1}"/>'
room+='''<path d="M35 155Q100 150 160 95 M35 155Q83 207 154 234 M35 155Q115 157 220 161 M76 135Q78 154 64 180 M119 116Q126 166 103 209 M165 94Q181 175 151 232" fill="none" stroke="#c8a1c9" stroke-width="2" opacity=".36"/>
<path d="M949 24V142 M912 36V104" stroke="#d8a478" stroke-width="2" opacity=".65"/>
<use href="#star" x="949" y="151"/><use href="#star" x="912" y="115"/>
<ellipse cx="540" cy="1210" rx="460" ry="230" fill="url(#mist)"/>
'''

# Exact illustrated silhouette in reference coordinates. The source JPEG is never edited.
outline='''M397 302 C383 259 389 198 414 172 C444 142 498 135 540 151 C557 112 614 84 666 99 C716 82 782 58 815 66 C848 76 859 102 881 117 C918 129 938 161 950 189 L940 232 L935 240 L942 254 L960 265 L950 277 L957 293 L940 288 L926 296 L926 280 L918 275 L922 263 L932 256 L930 236 L923 220 C888 200 875 204 858 199 C865 237 875 272 872 314 C903 311 915 328 912 352 C907 374 900 384 885 386 C907 409 945 409 955 450 L949 463 C965 478 1003 487 1003 508 C1004 535 954 558 901 565 C901 602 889 636 863 651 L880 686 L858 696 C907 720 938 752 950 776 C969 772 985 781 980 804 C969 838 952 857 922 867 C909 881 903 892 901 910 C909 965 885 1018 846 1040 C802 1066 720 1068 674 1054 C648 1085 561 1076 518 1049 L485 1032 C433 1038 384 1050 346 1030 C307 1008 308 977 312 941 C309 895 315 864 344 839 L283 826 L274 811 C300 788 320 759 339 731 L357 699 L355 691 L389 669 L373 652 L404 635 C389 632 376 627 369 617 C373 588 386 563 388 536 C389 507 396 486 402 465 C361 455 336 437 330 412 C319 386 320 353 344 332 C361 316 380 308 397 302Z'''
hero=f'''<defs><clipPath id="rabbit-cut"><path d="{outline}"/></clipPath></defs>
<ellipse cx="540" cy="1315" rx="270" ry="38" fill="#140e1b" opacity=".48" filter="url(#soft)"/>
<g transform="translate(6 401) scale(.85)"><g id="rabbit"><image href="assets/character.jpg" width="1254" height="1254" clip-path="url(#rabbit-cut)"/></g></g>'''

props=''
for i,(x,y,s) in enumerate([(130,925,.72),(949,1060,.83)]):
    props+=f'<g transform="translate({x} {y}) scale({s})"><g id="ghost-{i}" filter="url(#shadow)"><use href="#ghost"/></g></g>'

# Table in perspective with a generously sized lower title area.
props+='''<ellipse cx="540" cy="1430" rx="560" ry="210" fill="url(#warm)" opacity=".3"/>
<path d="M100 1354 Q540 1308 980 1354 L1043 1457 Q540 1510 37 1457Z" fill="url(#wood)" stroke="#a57885" stroke-width="5"/>
<path d="M37 1457 Q540 1510 1043 1457 L1043 1490 Q540 1540 37 1490Z" fill="#2c1c32" stroke="#70495f" stroke-width="3"/>
<path d="M333 1337 Q540 1320 746 1337 L820 1478 Q540 1508 260 1478Z" fill="#4a2859" stroke="#b48b9d" stroke-width="2"/>
<ellipse cx="540" cy="1414" rx="155" ry="45" fill="none" stroke="#bf91a2" opacity=".45" stroke-width="2"/>
'''
for i in range(5):
    props+=f'<g transform="translate({390+i*44} {1350+abs(i-2)*6})"><g id="table-card-{i}" class="table-card" transform="rotate({(i-2)*10} 45 70) scale(.66)"><use href="#card"/></g></g>'
props+='''<g transform="translate(587 1350)"><g id="chosen-card"><use href="#card" transform="rotate(16 45 70) scale(.66)"/></g></g>
<g transform="translate(195 1370)">
<ellipse cx="0" cy="51" rx="132" ry="30" fill="#1b111e" opacity=".6"/>
<path d="M-99 -49 Q-120 58 -43 74 L43 74 Q120 58 99 -49Z" fill="url(#pot)" stroke="#a27395" stroke-width="4"/>
<path d="M-62 61L-75 87 M62 61L75 87" stroke="#3a253b" stroke-width="15" stroke-linecap="round"/>
<path d="M-102 -27Q-144 -37 -131 6Q-120 23 -105 10 M102 -27Q144 -37 131 6Q120 23 105 10" fill="none" stroke="#805773" stroke-width="9"/>
<ellipse cy="-50" rx="105" ry="26" fill="#b479ab" stroke="#9b7196" stroke-width="7"/>
<ellipse cy="-50" rx="93" ry="18" fill="#ecac88"/>
<ellipse cy="-48" rx="82" ry="11" fill="#ffd0a3" opacity=".65"/>
<path d="M-70 -15Q-71 30 -43 43" fill="none" stroke="#d8a4bc" opacity=".25" stroke-width="9" stroke-linecap="round"/>
<path d="M0 -4L8 11 24 14 12 26 16 42 0 33 -16 42 -12 26 -24 14 -8 11Z" fill="none" stroke="#b58b9e" stroke-width="3"/>
<g id="potion-glow"><ellipse cy="-62" rx="140" ry="110" fill="url(#warm)"/></g>
'''
for i in range(5):props+=f'<circle class="bubble" cx="{-48+i*23}" cy="-55" r="{4+i%3*2}" fill="#ffe7bb" opacity=".6"/>'
for i in range(3):props+=f'<path class="steam" d="M{-40+i*38} -75 Q{-75+i*38} -112 {-35+i*38} -149 T{-35+i*38} -235" fill="none" stroke="#d9b7dd" stroke-width="{12+i*3}" opacity=".21" filter="url(#soft)"/>'
props+='</g>'
# Small foreground pumpkin, separate from the original character artwork.
props+='''<g transform="translate(948 1322)"><ellipse cy="25" rx="78" ry="18" fill="#180f20" opacity=".35"/><path d="M-4 -66Q-16 -88 9 -98" fill="none" stroke="#85555a" stroke-width="13" stroke-linecap="round"/><ellipse cx="-33" cy="-20" rx="36" ry="48" fill="#c97555"/><ellipse cx="33" cy="-20" rx="36" ry="48" fill="#d8895c"/><ellipse cy="-20" rx="39" ry="52" fill="#efaa70"/><path d="M-15 -59Q-35 -25 -17 16 M18 -57Q37 -23 18 17" fill="none" stroke="#ffd39a" opacity=".35" stroke-width="4"/><ellipse cx="-20" cy="-17" rx="6" ry="9" fill="#65405b"/><ellipse cx="20" cy="-17" rx="6" ry="9" fill="#65405b"/><path d="M-10 4Q0 18 10 4" stroke="#65405b" stroke-width="5" fill="none" stroke-linecap="round"/></g>'''
for i,(x,y,h) in enumerate([(858,1357,120),(950,1400,86),(65,1200,90)]):
    props+=f'''<g transform="translate({x} {y})"><g class="candle-glow"><ellipse cy="{-h-22}" rx="160" ry="190" fill="url(#warm)"/></g><ellipse cy="8" rx="44" ry="12" fill="#b08077"/><path d="M-27 0V{-h}H27V0Q0 10 -27 0" fill="#c398c4" stroke="#e9c3cf" stroke-width="2"/><path d="M-26 {-h}Q-20 {-h+12} -11 {-h+5}V{-h+38}Q-5 {-h+50} 1 {-h+36}V{-h+7}Q16 {-h+15} 26 {-h}" fill="#f4d7ca"/><ellipse cy="{-h}" rx="27" ry="8" fill="#f7e2ca"/><path d="M0 {-h+2}V{-h-18}" stroke="#5c3c46" stroke-width="3"/><g transform="translate(0 {-h-17})"><path class="flame" d="M0 3 C-25 -11 -13 -30 0 -51 C3 -29 23 -19 12 -4 Q7 3 0 3" fill="url(#flame)" filter="url(#glow)"/></g></g>'''

for i in range(25):
    x=60+(i*139)%970;y=250+(i*179)%1190
    props+=f'<g transform="translate({x} {y}) scale({.3+(i%4)*.13})"><g class="spark"><use href="#star"/></g></g>'

html='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MaeMorKratai Halloween 2026</title><style>
@font-face{font-family:Brand;src:url('assets/georgia.ttf')}*{box-sizing:border-box}html,body{margin:0;width:1080px;height:1920px;background:#1c102c;overflow:hidden}
#halloween{position:relative;width:1080px;height:1920px;overflow:hidden;background:#1c102c;perspective:1600px}
#camera{position:absolute;inset:0;transform-style:preserve-3d;transform-origin:50% 54%}.plane{position:absolute;inset:0;width:1080px;height:1920px}.plane svg{display:block;width:1080px;height:1920px}
#room{transform:translateZ(-55px) scale(1.07)}#mascot{transform:translateZ(20px) scale(.987)}#props{transform:translateZ(58px) scale(.965)}
.vignette{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 46%,transparent 42%,#160e24bb 100%);pointer-events:none}
.scene-content{position:relative;display:flex;flex-direction:column;align-items:center;width:100%;height:100%;padding:1500px 75px 130px;gap:20px;pointer-events:none;background:linear-gradient(transparent 74%,#1c102cbb 82%,#1c102c 100%)}
#wordmark{font:64px Brand,Georgia,serif;letter-spacing:1px;color:#fff0cf;white-space:nowrap;text-shadow:0 2px 20px #ef985833;margin:0}#subtitle{font:31px Brand,Georgia,serif;letter-spacing:6px;color:#f4bd8c;margin:0}.ornament{width:270px;height:32px;color:#dfb58b;flex-shrink:0}.overline{color:#d9aec8;font:17px Brand,Georgia,serif;letter-spacing:7px;margin-bottom:7px}
</style></head><body><div id="halloween" data-composition-id="maemorkratai-halloween" data-start="0" data-duration="12" data-width="1080" data-height="1920" data-fps="30"><div id="camera">'''
for id,svg in [('room',room),('mascot',hero),('props',props)]:
    # Unique gradient/filter identifiers per SVG to avoid duplicate DOM IDs.
    import re
    names=re.findall(r'id="([^"]+)"',defs)
    content=defs+svg
    for name in names:
        content=content.replace(f'id="{name}"',f'id="{id}-{name}"').replace(f'url(#{name})',f'url(#{id}-{name})').replace(f'href="#{name}"',f'href="#{id}-{name}"')
    html+=f'<div class="plane" id="{id}"><svg viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg"><g data-layout-allow-overflow="true" filter="url(#{id}-paper)">{content}</g></svg></div>'
html+='''</div><div class="vignette"></div><div class="scene-content"><svg class="ornament" id="title-star" viewBox="0 0 270 32"><path d="M0 16H110 M160 16H270 M135 0Q137 14 150 16Q137 18 135 32Q133 18 120 16Q133 14 135 0" stroke="currentColor" fill="currentColor" opacity=".85"/></svg><h1 id="wordmark">MaeMorKratai</h1><p id="subtitle">Halloween 2026</p></div></div><script src="assets/gsap.min.js"></script><script>
const tl=gsap.timeline({paused:true});
// Layout above is the visible hero frame; all entrances are derived from it.
tl.fromTo('#camera',{rotationY:-.9,rotationX:.4,scale:1.025},{rotationY:.8,rotationX:-.35,scale:1,duration:12,ease:'sine.inOut'},0);
tl.to('#rabbit',{y:-7,rotation:.4,svgOrigin:'630 1040',duration:2,repeat:5,yoyo:true,ease:'sine.inOut'},0);
tl.to('#ghost-0',{y:-31,x:15,rotation:7,svgOrigin:'0 0',duration:2,repeat:5,yoyo:true,ease:'sine.inOut'},0);
tl.fromTo('#ghost-1',{y:-20,rotation:4},{y:17,x:-17,rotation:-7,svgOrigin:'0 0',duration:2.4,repeat:4,yoyo:true,ease:'sine.inOut'},0);
document.querySelectorAll('.flame').forEach((el,i)=>tl.to(el,{scaleX:.78,scaleY:1.16,rotation:i%2?6:-6,svgOrigin:'0 0',duration:.3+i*.1,repeat:Math.floor(12/(.3+i*.1))-1,yoyo:true,ease:'sine.inOut'},0));
tl.to('.candle-glow',{opacity:.55,duration:.6,repeat:19,yoyo:true,ease:'sine.inOut'},0);
tl.to('#potion-glow',{opacity:.35,duration:1.5,repeat:7,yoyo:true,ease:'sine.inOut'},0);
document.querySelectorAll('.bubble').forEach((el,i)=>tl.fromTo(el,{y:0,opacity:0,scale:.5},{y:-105-i*7,opacity:.8,scale:1.2,duration:1.3+i*.16,repeat:Math.floor((12-i*.2)/(1.3+i*.16))-1,ease:'power1.out'},i*.2));
document.querySelectorAll('.steam').forEach((el,i)=>tl.to(el,{y:-17,x:10-i*9,opacity:.08,duration:2+i*.2,repeat:Math.floor(12/(2+i*.2))-1,yoyo:true,ease:'sine.inOut'},0));
document.querySelectorAll('.spark').forEach((el,i)=>tl.fromTo(el,{opacity:.15},{opacity:.9,duration:.7+i%4*.1,repeat:Math.floor(12/(.7+i%4*.1))-1,yoyo:true,ease:'sine.inOut'},0));
tl.to('.table-card',{y:-5,stagger:.13,duration:.7,yoyo:true,repeat:1,ease:'sine.inOut'},2.4);
tl.to('#chosen-card',{x:36,y:-155,rotation:-15,svgOrigin:'30 45',duration:1.8,ease:'sine.inOut'},4.8);
tl.to('#chosen-card',{y:-165,rotation:-10,duration:1,repeat:1,yoyo:true,ease:'sine.inOut'},6.6);
tl.to('#chosen-card',{y:0,x:0,rotation:0,duration:1.4,ease:'sine.inOut'},8.6);
tl.from('#title-star',{opacity:0,scaleX:.5,transformOrigin:'50% 50%',duration:1.1,ease:'sine.out'},7.7);
tl.from('#wordmark',{opacity:0,y:18,duration:1.1,ease:'power2.out'},8.05);
tl.from('#subtitle',{opacity:0,y:13,duration:1,ease:'power2.out'},8.45);
window.__timelines=window.__timelines||{};window.__timelines['maemorkratai-halloween']=tl;
</script></body></html>'''
(P/'index.html').write_text(html)
(P/'hyperframes.json').write_text(json.dumps({'$schema':'https://hyperframes.heygen.com/schema.json','entry':'index.html'},indent=2))
(P/'meta.json').write_text(json.dumps({'id':'maemorkratai-halloween','name':'MaeMorKratai Halloween 2026','width':1080,'height':1920,'fps':30,'duration':DURATION},indent=2))
print(f'Built {P}/index.html')

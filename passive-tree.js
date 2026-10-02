/* Interactive read-only guide tree. Atlas/arc conventions adapted from the
 * MIT-licensed poe2-tools/poe2-build-planner; license embedded in the guide. */
const passiveTree = (() => {
 const root=$('passive-tree'),canvas=$('passive-canvas'),ctx=canvas.getContext('2d');
 const nodes=Object.entries(PASSIVE.nodes).map(([key,n])=>({...n,key:Number(key)}));
 const byId=new Map(nodes.map(n=>[n.key,n]));
 const edges=[];for(const n of nodes)for(const id of n.links){if(n.key<id&&byId.has(id))edges.push([n,byId.get(id)]);}
 const imgs={};let width=0,height=0,scale=.2,cx=0,cy=0,view='main',filter='all',stage=-1;
 let common=new Set(),one=new Set(),two=new Set(),selected=null,hovered=null,framePending=false,initialFit=false,autoFit=true;
 const pointers=new Map();let moved=false,gesture=null;
 const tooltip=$('tree-hover');let tooltipNode=null;
 // Keep the floating card outside the canvas panel's clipping boundary.
 document.body.append(tooltip);
 tooltip.setAttribute('role','tooltip');
 function hideTooltip(){tooltip.hidden=true;tooltipNode=null;canvas.removeAttribute('aria-describedby');}
 const nodeName=n=>n.isAscendancyStart?label('treeAscName'):n.key===50986?label('treeClassName'):n.classStartIndex?label('treeClassStart')+' · '+n.name:term(n);
 const nodeHint=n=>label(n.isJewelSocket?'treeJewelHint':n.classStartIndex||n.isAscendancyStart?'treeStartHint':'treeChoiceHint');
 function hoverDetail(n,e){
  if(!n||e.pointerType==='touch'){hideTooltip();return;}
  if(tooltipNode!==n){
   const stats=translatedStats(n);tooltipNode=n;
   tooltip.innerHTML=`<div class="tree-tooltip-header"><span class="tree-node-type">${nodeType(n)}</span><h3>${esc(nodeName(n))}</h3><div class="tree-node-en">${esc(n.name)}</div><span class="tree-allocation" style="--node-color:${color(mask(n)||1)}">${esc(allocation(n))}</span></div><div class="tree-tooltip-body">${stats.length?`<ul>${stats.map(s=>`<li>${esc(s)}</li>`).join('')}</ul>`:`<p>${esc(nodeHint(n))}</p>`}</div><div class="tree-tooltip-footer">${esc(label('treeHoverHint'))}</div>`;
  }
  tooltip.hidden=false;canvas.setAttribute('aria-describedby',tooltip.id);
  const margin=12,gap=18,rect=tooltip.getBoundingClientRect();
  let left=e.clientX+gap,top=e.clientY+gap;
  if(left+rect.width>window.innerWidth-margin)left=e.clientX-rect.width-gap;
  if(top+rect.height>window.innerHeight-margin)top=e.clientY-rect.height-gap;
  tooltip.style.left=Math.max(margin,Math.min(left,window.innerWidth-rect.width-margin))+'px';
  tooltip.style.top=Math.max(margin,Math.min(top,window.innerHeight-rect.height-margin))+'px';
 }
 for(const [key,url] of Object.entries(PASSIVE.images)){const img=new Image();imgs[key]=img;img.onload=drawSoon;img.src=url;}
 const clean=text=>text.replace(/\[([^\]|]+)\|([^\]]+)\]/g,'$2').replace(/\[([^\]]+)\]/g,'$1').replace(/<[^>]+>/g,'').replace(/[{}]/g,'');
 const term=n=>PASSIVE.terms[n.name]?.[language]||n.name;
 const translatedStats=n=>n.stats.map(s=>PASSIVE.stats[s]?.[language]||clean(s));
 const inView=n=>view==='asc'?!!n.ascendancyId:!n.ascendancyId;
 const mask=n=>common.has(n.key)?1:(one.has(n.key)?2:0)|(two.has(n.key)?4:0);
 const visibleMask=n=>{let m=mask(n);if(filter==='set1')m&=3;else if(filter==='set2')m&=5;return m;};
 const isActive=n=>visibleMask(n)||n.key===50986||n.isAscendancyStart;
 const color=m=>m&1?'#d7b878':m===6?'#c8cdca':m&2?'#eb9871':'#75bec9';
 const nodeType=n=>label(n.isAscendancyStart?'treeAscStart':n.classStartIndex?'treeClassStart':n.isJewelSocket?'treeJewel':n.isMultipleChoiceOption?'treeChoice':n.ascendancyId?'treeAscNode':n.isKeystone?'treeKeystone':n.isNotable?'treeNotable':'treeSmall');
 const allocation=n=>{const m=mask(n);return m===1?label('treeShared'):m===6?label('treeBoth'):m===2?label('treeSet1'):m===4?label('treeSet2'):label('treeUnallocated');};
 const radius=n=>n.isAscendancyStart?95:n.classStartIndex?90:n.isKeystone?57:n.isNotable?45:n.isJewelSocket?40:23;
 function drawSoon(){if(framePending)return;framePending=true;requestAnimationFrame(()=>{framePending=false;draw();});}
 function worldPoint(x,y){return {x:(x-width/2)/scale+cx,y:(y-height/2)/scale+cy};}
 function screenPoint(n){return {x:(n.x-cx)*scale+width/2,y:(n.y-cy)*scale+height/2};}
 function sprite(atlas,key,x,y,size,alpha=1){const f=PASSIVE.atlases[atlas][key],img=imgs[atlas];if(!f||!img?.complete||!img.naturalWidth)return false;ctx.globalAlpha=alpha;ctx.drawImage(img,f.x,f.y,f.w,f.h,x-size/2,y-size/2,size,size);ctx.globalAlpha=1;return true;}
 function path(a,b){
  ctx.beginPath();ctx.moveTo(a.x,a.y);
  const g=PASSIVE.groups[a.group];
  if(g&&a.group===b.group&&a.orbit===b.orbit&&a.orbit>0){
   const r=Math.hypot(a.x-g.x,a.y-g.y),start=Math.atan2(a.y-g.y,a.x-g.x),end=Math.atan2(b.y-g.y,b.x-g.x);
   let delta=end-start;while(delta>Math.PI)delta-=2*Math.PI;while(delta<-Math.PI)delta+=2*Math.PI;
   ctx.arc(g.x,g.y,r,start,start+delta,delta<0);
  }else ctx.lineTo(b.x,b.y);
  ctx.stroke();
 }
 function draw(){
  if(!width||!height)return;
  const dpr=Math.min(window.devicePixelRatio||1,2);ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,width,height);
  const bg=ctx.createRadialGradient(width*.45,height*.55,0,width*.45,height*.55,width*.8);bg.addColorStop(0,'#1a2831');bg.addColorStop(1,'#0b121a');ctx.fillStyle=bg;ctx.fillRect(0,0,width,height);
  ctx.save();ctx.translate(width/2,height/2);ctx.scale(scale,scale);ctx.translate(-cx,-cy);
  if(view==='main'){
   const n=byId.get(50986);sprite('background','classMercenary:Class0',n.x,n.y,1000,.38);
  }else{
   const n=nodes.find(n=>n.isAscendancyStart);sprite('background','classMercenary:Class3',n.x,n.y,1800,.36);
  }
  const pad=160/scale,minx=cx-width/(2*scale)-pad,maxx=cx+width/(2*scale)+pad,miny=cy-height/(2*scale)-pad,maxy=cy+height/(2*scale)+pad;
  const onscreen=n=>n.x>=minx&&n.x<=maxx&&n.y>=miny&&n.y<=maxy;
  ctx.lineWidth=1/scale;ctx.strokeStyle='#35434b';ctx.globalAlpha=.5;
  for(const [a,b] of edges)if(inView(a)&&(onscreen(a)||onscreen(b)))path(a,b);
  ctx.globalAlpha=1;
  for(const [a,b] of edges){if(!inView(a)||(!onscreen(a)&&!onscreen(b)))continue;const ma=visibleMask(a)||((a.key===50986||a.isAscendancyStart)?1:0),mb=visibleMask(b)||((b.key===50986||b.isAscendancyStart)?1:0);if(!ma||!mb)continue;
   // A common node may connect to either weapon path. Exclusive sets never connect to each other.
   const m=ma&1?mb:mb&1?ma:ma&mb;if(!m)continue;
   ctx.strokeStyle=color(m);ctx.lineWidth=2.4/scale;path(a,b);
  }
  for(const n of nodes){if(!inView(n)||!onscreen(n))continue;const active=isActive(n),r=radius(n);if(scale<.05){const dot=Math.max(active?(n.isNotable||n.isKeystone?3:1.9):.65,r*scale*.5);ctx.beginPath();ctx.arc(n.x,n.y,dot/scale,0,Math.PI*2);ctx.fillStyle=active?color(visibleMask(n)||1):'#46535a';ctx.globalAlpha=active?1:.42;ctx.fill();ctx.globalAlpha=1;if(n===selected||n===hovered){ctx.beginPath();ctx.arc(n.x,n.y,(dot+3)/scale,0,Math.PI*2);ctx.lineWidth=1.5/scale;ctx.strokeStyle='#f9edcc';ctx.stroke();}continue;}const size=Math.max(r*2,((n.isNotable||n.isKeystone)?10:5)/scale);
   const m=visibleMask(n);if(active){ctx.beginPath();ctx.arc(n.x,n.y,size*.54,0,Math.PI*2);ctx.fillStyle='rgba(215,184,120,.14)';ctx.fill();}
   const key=(n.isKeystone?'keystoneActive':n.isNotable?'notableActive':'normalActive')+':'+n.icon;
   const hasIcon=sprite('skills',key,n.x,n.y,size*.72,active?1:.42);
   if(!hasIcon){ctx.beginPath();ctx.arc(n.x,n.y,size*.31,0,Math.PI*2);ctx.fillStyle=active?'#bb9560':'#2d3b43';ctx.fill();}
   const frame=n.isAscendancyStart?'AscendancyStartNode':n.ascendancyId?'AscendancyFrame'+(n.isNotable?'Notable':'Normal')+(active?'Allocated':'Unallocated'):n.isKeystone?'KeystoneFrame'+(active?'Allocated':'Unallocated'):n.isNotable?'NotableFrame'+(active?'Allocated':'Unallocated'):n.isJewelSocket?'JewelFrame'+(active?'Allocated':'Unallocated'):'PSSkillFrame'+(active?'Active':'');
   sprite('frame','frame:'+frame,n.x,n.y,size,active?1:.62);
   if(m&6){ctx.lineWidth=2.5/scale;ctx.beginPath();ctx.arc(n.x,n.y,size*.53,0,Math.PI*2);ctx.strokeStyle=color(m);ctx.stroke();if(m===6){ctx.beginPath();ctx.arc(n.x,n.y,size*.53,Math.PI/2,Math.PI*1.5);ctx.strokeStyle='#eb9871';ctx.stroke();ctx.beginPath();ctx.arc(n.x,n.y,size*.53,-Math.PI/2,Math.PI/2);ctx.strokeStyle='#75bec9';ctx.stroke();}}
   if(n===selected||n===hovered){ctx.beginPath();ctx.arc(n.x,n.y,size*.65,0,Math.PI*2);ctx.lineWidth=2/scale;ctx.strokeStyle=n===selected?'#f9edcc':'#a4d1c8';ctx.stroke();}
  }
  ctx.restore();$('tree-zoom').textContent=Math.round(scale*100)+'%';
 }
 function fit(whole=false){
  hideTooltip();
  const pool=nodes.filter(n=>inView(n)&&(whole||isActive(n)));if(!pool.length||!width)return;
  const minx=Math.min(...pool.map(n=>n.x)),maxx=Math.max(...pool.map(n=>n.x)),miny=Math.min(...pool.map(n=>n.y)),maxy=Math.max(...pool.map(n=>n.y));
  cx=(minx+maxx)/2;cy=(miny+maxy)/2;
  scale=Math.max(.015,Math.min(.55,(width-90)/Math.max(300,maxx-minx+200),(height-90)/Math.max(300,maxy-miny+200)));initialFit=true;autoFit=true;drawSoon();
 }
 function zoom(factor,x=width/2,y=height/2){hideTooltip();autoFit=false;const before=worldPoint(x,y);scale=Math.max(.015,Math.min(1.8,scale*factor));cx=before.x-(x-width/2)/scale;cy=before.y-(y-height/2)/scale;drawSoon();}
 function pick(x,y){let found=null,best=Infinity;for(const n of nodes){if(!inView(n))continue;const p=screenPoint(n),d=Math.hypot(p.x-x,p.y-y),r=Math.max(6,radius(n)*scale);if(d<r+3&&d<best){found=n;best=d;}}return found;}
 function detail(n,pin=false){
  if(!n){$('tree-detail').innerHTML=`<p class="tree-empty">${label('treeInspectHint')}</p>`;return;}
  const stats=translatedStats(n);const name=nodeName(n);
  $('tree-detail').innerHTML=`<div class="tree-detail-top"><span class="tree-node-type">${nodeType(n)}</span>${pin?`<button id="tree-unpin" type="button" aria-label="${label('treeUnpin')}">×</button>`:''}</div><h3>${esc(name)}</h3><div class="tree-node-en">${esc(n.name)}</div><span class="tree-allocation" style="--node-color:${color(mask(n)||1)}">${esc(allocation(n))}</span>${stats.length?`<ul>${stats.map(s=>`<li>${esc(s)}</li>`).join('')}</ul>`:`<p class="fineprint">${esc(nodeHint(n))}</p>`}${PASSIVE.terms[n.name]?.url?`<a class="tree-db-link" href="${esc(PASSIVE.terms[n.name].url)}" target="_blank" rel="noopener">${label('treeDatabase')} ↗</a>`:''}<details><summary>${label('treeEnglish')}</summary><ul>${n.stats.map(s=>`<li>${esc(clean(s))}</li>`).join('')}</ul><small>ID ${n.key} · ${esc(n.id)}</small></details>`;
  if(pin)$('tree-unpin').addEventListener('click',()=>{selected=null;detail(hovered);drawSoon();});
 }
 function inspect(n,focus=true){hideTooltip();selected=n;hovered=null;autoFit=false;if(n){view=n.ascendancyId?'asc':'main';if(focus){cx=n.x;cy=n.y;scale=Math.max(scale,n.ascendancyId ? .35 : .45);}}updateViewButtons();detail(n,true);$('tree-status').textContent=n?term(n)+' · '+allocation(n):'';drawSoon();}
 function results(){
  const q=$('tree-search').value.trim().toLocaleLowerCase();let matches=nodes.filter(n=>q?(term(n)+' '+n.name+' '+translatedStats(n).join(' ')).toLocaleLowerCase().includes(q):visibleMask(n)&&(n.isNotable||n.isKeystone||n.isJewelSocket||n.ascendancyId)&&!n.isAscendancyStart);
  matches.sort((a,b)=>Number(!!mask(b))-Number(!!mask(a))||term(a).localeCompare(term(b)));const total=matches.length;matches=matches.slice(0,q?60:80);
  $('tree-result-count').textContent=q?label('treeResults').replace('{n}',total)+(total>60?' · '+label('treeResultsLimit'):''):label('treeAllocatedList');
  $('tree-results').innerHTML=matches.length?matches.map(n=>`<button type="button" data-node="${n.key}" class="tree-result"><span>${esc(term(n))}</span><small>${esc(n.name)} · ${esc(allocation(n))}</small></button>`).join(''):`<p class="fineprint">${label('treeNoResults')}</p>`;
 }
 function updateViewButtons(){document.querySelectorAll('[data-tree-view]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.treeView===view));}
 function refresh(){
  hideTooltip();
  const changed=stage!==currentStage;stage=currentStage;const s=PASSIVE.stages[stage];common=new Set(s.common);one=new Set(s.set1);two=new Set(s.set2);
  $('tree-stage').innerHTML=c().stages.map((s,i)=>`<option value="${i}">${esc(s.label)} · ${esc(s.name)}</option>`).join('');$('tree-stage').value=stage;
  $('tree-stage').setAttribute('aria-label',label('treeStageLabel'));$('tree-filter').setAttribute('aria-label',label('treeFilterLabel'));
  $('tree-filter').innerHTML=['all','set1','set2'].map((v,i)=>`<option value="${v}">${label(['treeAll','treeSet1','treeSet2'][i])}</option>`).join('');$('tree-filter').value=filter;
  $('tree-cn').setAttribute('aria-pressed',language==='cn');$('tree-tw').setAttribute('aria-pressed',language==='tw');$('tree-search').placeholder=label('treeSearch');$('tree-search').setAttribute('aria-label',label('treeSearch'));
  canvas.setAttribute('aria-label',label('treeCanvasLabel'));$('tree-in').setAttribute('aria-label',label('treeZoomIn'));$('tree-out').setAttribute('aria-label',label('treeZoomOut'));
  root.querySelectorAll('[data-label]').forEach(e=>e.textContent=label(e.dataset.label));
  const all=new Set([...s.common,...s.set1,...s.set2]);const normal=[...all].filter(i=>!byId.get(i).ascendancyId&&!byId.get(i).classStartIndex).length;
  const asc=[...all].filter(i=>byId.get(i).ascendancyId&&!byId.get(i).isAscendancyStart&&!byId.get(i).isMultipleChoiceOption).length;
  $('tree-counts').innerHTML=`<span><b>${normal}</b>${label('treeNormalCount')}</span><span><b>${one.size}</b>${label('treeSet1Short')}</span><span><b>${two.size}</b>${label('treeSet2Short')}</span><span><b>${asc}</b>${label('treeAscCount')}</span>`;
  $('tree-stage-title').textContent=c().stages[stage].label;
  $('tree-expand').textContent=label(root.classList.contains('tree-expanded')?'treeClose':'treeExpand');updateViewButtons();if(changed){selected=null;hovered=null;$('tree-search').value='';fit();}detail(selected||hovered,!!selected);results();drawSoon();
 }
 $('tree-cn').addEventListener('click',()=>setLanguage('cn'));$('tree-tw').addEventListener('click',()=>setLanguage('tw'));
 $('tree-stage').addEventListener('change',e=>{currentStage=Number(e.target.value);save('stage',currentStage);renderStage();});
 $('tree-filter').addEventListener('change',e=>{hideTooltip();filter=e.target.value;results();drawSoon();});
 $('tree-search').addEventListener('input',results);
 $('tree-results').addEventListener('click',e=>{const button=e.target.closest('[data-node]');if(button)inspect(byId.get(Number(button.dataset.node)));});
 root.querySelectorAll('[data-tree-view]').forEach(b=>b.addEventListener('click',()=>{hideTooltip();view=b.dataset.treeView;selected=null;hovered=null;updateViewButtons();detail(null);fit();}));
 $('tree-fit').addEventListener('click',()=>fit());$('tree-whole').addEventListener('click',()=>{view='main';updateViewButtons();fit(true);});
 $('tree-in').addEventListener('click',()=>zoom(1.3));$('tree-out').addEventListener('click',()=>zoom(1/1.3));
 function expand(value){hideTooltip();root.classList.toggle('tree-expanded',value);$('tree-expand').setAttribute('aria-expanded',value);$('tree-expand').textContent=label(value?'treeClose':'treeExpand');document.body.classList.toggle('tree-open',value);}
 $('tree-expand').addEventListener('click',()=>expand(!root.classList.contains('tree-expanded')));
 document.addEventListener('keydown',e=>{if(e.key==='Escape'){hideTooltip();if(root.classList.contains('tree-expanded'))expand(false);selected=null;hovered=null;detail(null);drawSoon();}});
 canvas.addEventListener('keydown',e=>{const keys=['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','=','-','Home'];if(!keys.includes(e.key))return;e.preventDefault();hideTooltip();if(e.key==='Home')fit();else if(e.key==='+'||e.key==='=')zoom(1.3);else if(e.key==='-')zoom(1/1.3);else{autoFit=false;cx+=(e.key==='ArrowRight'?100:e.key==='ArrowLeft'?-100:0)/scale;cy+=(e.key==='ArrowDown'?100:e.key==='ArrowUp'?-100:0)/scale;drawSoon();}});
 function point(e){const r=canvas.getBoundingClientRect();return{x:e.clientX-r.left,y:e.clientY-r.top};}
 canvas.addEventListener('wheel',e=>{e.preventDefault();const p=point(e);zoom(Math.exp(-Math.max(-100,Math.min(100,e.deltaY))*.0025),p.x,p.y);},{passive:false});
 canvas.addEventListener('pointerdown',e=>{if(e.button>0)return;hideTooltip();canvas.focus({preventScroll:true});canvas.setPointerCapture(e.pointerId);const p=point(e);pointers.set(e.pointerId,p);moved=false;if(pointers.size===2){const a=[...pointers.values()];gesture={distance:Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y),scale};moved=true;}canvas.classList.add('dragging');});
 canvas.addEventListener('pointermove',e=>{const p=point(e),old=pointers.get(e.pointerId);
  if(old){pointers.set(e.pointerId,p);if(pointers.size===2&&gesture){const a=[...pointers.values()],d=Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y);zoom((gesture.scale*d/Math.max(1,gesture.distance))/scale,(a[0].x+a[1].x)/2,(a[0].y+a[1].y)/2);moved=true;}
   else{const dx=p.x-old.x,dy=p.y-old.y;if(Math.hypot(dx,dy)>2)moved=true;autoFit=false;cx-=dx/scale;cy-=dy/scale;drawSoon();}return;}
  const n=pick(p.x,p.y);if(n!==hovered){hovered=n;canvas.style.cursor=n?'pointer':'grab';if(!selected)detail(n);drawSoon();}hoverDetail(n,e);
 });
 function endPointer(e){if(!pointers.has(e.pointerId))return;const p=point(e);pointers.delete(e.pointerId);if(!pointers.size){canvas.classList.remove('dragging');if(!moved&&e.type!=='pointercancel'){const n=pick(p.x,p.y);if(n)inspect(n,false);}gesture=null;}else moved=true;}
 canvas.addEventListener('pointerup',endPointer);canvas.addEventListener('pointercancel',endPointer);canvas.addEventListener('pointerleave',()=>{if(!pointers.size){hovered=null;hideTooltip();if(!selected)detail(null);drawSoon();}});
 window.addEventListener('scroll',hideTooltip,{capture:true,passive:true});
 window.addEventListener('blur',hideTooltip);
 new ResizeObserver(()=>{hideTooltip();const rect=canvas.getBoundingClientRect();width=rect.width;height=rect.height;const dpr=Math.min(window.devicePixelRatio||1,2);canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);if((!initialFit||autoFit)&&stage>=0)fit();drawSoon();}).observe(canvas);
 return {refresh};
})();

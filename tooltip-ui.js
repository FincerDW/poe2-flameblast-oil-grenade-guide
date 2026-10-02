// All popovers use locally embedded, observed source snapshots.
const tipPanel=$('game-tooltip');
let tipAnchor=null,tipPinned=false,tipTimer;
const tipText=(cn,tw)=>language==='tw'?tw:cn;
function tipAttrs(key){return key?`data-tip="${key}" aria-haspopup="dialog" aria-controls="game-tooltip" aria-expanded="false"`:''}
function hideTip(restore=false){
 clearTimeout(tipTimer);const old=tipAnchor;
 if(old)old.setAttribute('aria-expanded','false');
 tipPanel.hidden=true;tipPanel.innerHTML='';tipAnchor=null;tipPinned=false;
 if(restore&&old?.isConnected){old.focus({preventScroll:true});hideTip();}
}
function positionTip(){
 if(!tipAnchor||tipPanel.hidden)return;
 const r=tipAnchor.getBoundingClientRect(),w=tipPanel.offsetWidth,h=tipPanel.offsetHeight;
 if(window.innerWidth<=540){tipPanel.style.left='10px';tipPanel.style.top=Math.max(10,window.innerHeight-h-10)+'px';return}
 let x=r.right+12;if(x+w>window.innerWidth-12)x=r.left-w-12;
 x=Math.max(12,Math.min(x,window.innerWidth-w-12));
 const y=Math.max(12,Math.min(r.top-20,window.innerHeight-h-12));
 tipPanel.style.left=x+'px';tipPanel.style.top=y+'px';
}
function tipBlock(b,i){
 const lines=b.split('\n');
 if(i===0){const tags=[],stats=[];for(const l of lines){if(!/[：:\d]/.test(l)&&!stats.length)tags.push(l);else stats.push(l)}return `<div class="tip-block tip-stats"><div class="tip-tags">${tags.map(l=>`<span>${esc(l)}</span>`).join('')}</div>${esc(stats.join('\n'))}</div>`}
 return `<div class="tip-block">${esc(b)}</div>`;
}
function showTip(anchor,pin=false){
 clearTimeout(tipTimer);if(tipPinned&&tipAnchor!==anchor&&!pin)return;
 const key=anchor.dataset.tip,t=TOOLTIPS.tips[key];if(!t)return;
 if(tipAnchor===anchor&&!tipPanel.hidden){tipPinned=tipPinned||pin;return}
 hideTip();tipAnchor=anchor;tipPinned=pin;
 anchor.setAttribute('aria-expanded','true');
 const img=anchor.querySelector('img');
 const context=t.stage!==null?`${c().stages[t.stage].label} · ${label('slot_'+t.kind)}${t.set?' · '+label('set'+t.set):''}`:tipText('原文游戏提示','原文遊戲提示');
 const title=t[language]===t.en&&t.kind!=='named'?label('slot_'+t.kind):t[language];
 const blocks=t.body[language].split('\n\n').filter(Boolean);
 tipPanel.innerHTML=`<header class="tip-header">${img?`<img src="${img.src}" alt="">`:''}<div><div class="tip-kicker">${esc(context)}</div><h3 id="tip-title">${esc(title)}</h3><div class="tip-en">${esc(t.en)}</div></div><button type="button" class="tip-close" aria-label="${tipText('关闭提示','關閉提示')}">×</button></header><div class="tip-scroll">${blocks.map(tipBlock).join('')}${t.en==='Implanted Gems'?`<p class="tip-note">${tipText('原文提示只显示名称与天赋类型，未显示效果。','原文提示只顯示名稱與天賦類型，未顯示效果。')}</p>`:''}<p class="tip-note">${t.kind==='named'&&t.original.includes('Level:')?tipText('技能数值按原文等级区间显示；品质效果与正文分别保留原文数据。','技能數值按原文等級區間顯示；品質效果與正文分別保留原文資料。'):tipText('数值与词缀保留原文显示；装备提示为所注明阶段的配置示例。','數值與詞綴保留原文顯示；裝備提示為所註明階段的配置範例。')}</p><details class="tip-original"><summary>${tipText('展开英文原文','展開英文原文')}</summary><pre>${esc(t.original)}</pre></details><a class="tip-source" href="${t.stage!==null?c().stages[t.stage].url:'https://mobalytics.gg/poe-2/builds/fubgun-flameblast-oil-grenade'}" target="_blank" rel="noopener">Mobalytics · ${label('original')} ↗</a></div>`;
 tipPanel.hidden=false;positionTip();
}
function delayHide(){clearTimeout(tipTimer);if(!tipPinned)tipTimer=setTimeout(()=>hideTip(),220)}
document.addEventListener('mouseover',e=>{
 if(tipPanel.contains(e.target)){clearTimeout(tipTimer);return}
 const a=e.target.closest('[data-tip]');if(a&&(!e.relatedTarget||!a.contains(e.relatedTarget)))showTip(a);
});
document.addEventListener('mouseout',e=>{
 if(e.relatedTarget&&tipPanel.contains(e.relatedTarget)){clearTimeout(tipTimer);return}
 if(tipPanel.contains(e.target)){if(!tipPanel.contains(e.relatedTarget))delayHide();return}
 const a=e.target.closest('[data-tip]');if(a&&!a.contains(e.relatedTarget))delayHide();
});
document.addEventListener('focusin',e=>{const a=e.target.closest('[data-tip]');if(a)showTip(a);else if(!tipPanel.contains(e.target)&&!tipPinned)hideTip()});
document.addEventListener('focusout',e=>{if(!tipPinned&&(!e.relatedTarget||(!tipPanel.contains(e.relatedTarget)&&!e.relatedTarget.closest('[data-tip]'))))delayHide()});
document.addEventListener('click',e=>{
 const close=e.target.closest('.tip-close');if(close){hideTip(true);return}
 const a=e.target.closest('button[data-tip]');if(a){e.preventDefault();if(tipAnchor===a&&tipPinned)hideTip();else showTip(a,true);return}
 // A drag released over an icon may produce a click on its common ancestor.
 if(tipAnchor?.matches(':hover')&&e.target.contains(tipAnchor))return;
 if(!tipPanel.contains(e.target))hideTip();
});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!tipPanel.hidden){e.preventDefault();hideTip(true)}});
tipPanel.addEventListener('toggle',positionTip,true);
window.addEventListener('resize',positionTip);
window.addEventListener('scroll',()=>{if(tipPinned)positionTip();else hideTip()},{passive:true});

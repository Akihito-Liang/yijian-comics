/* The catalogue is the single source for chapter and episode navigation. */
const PROGRESS_KEY='yijian.reading.v1';
const $=s=>document.querySelector(s);
function readSaved(){
  const raw=localStorage.getItem(PROGRESS_KEY);
  if(!raw)return {};
  try {const value=JSON.parse(raw);return value&&typeof value==='object'&&!Array.isArray(value)?value:{}} catch(error){if(error instanceof SyntaxError)return {};throw error}
}
function pageNumber(value,max){const n=Number(value);return Number.isInteger(n)&&n>=1&&n<=max?n:1}
function readerURL(episode,page=1){return `read.html?episode=${encodeURIComponent(episode.id)}#page-${pageNumber(page,episode.pages)}`}
function imageURL(episode,page){return `${episode.base}page-${String(page).padStart(2,'0')}.png`}
function el(tag,className,text){const node=document.createElement(tag);if(className)node.className=className;if(text!==undefined)node.textContent=text;return node}
function link(text,href,className){const node=el('a',className,text);node.href=href;return node}

async function main(){
 const response=await fetch('catalog.json');if(!response.ok)throw new Error('无法读取卷章目录');
 const catalog=await response.json();
 const episodes=catalog.chapters.flatMap(ch=>ch.episodes.map(ep=>({...ep,chapter:ch})));
 const saved=readSaved();
 if(document.body.dataset.view==='shelf'){
  $('#library-count').textContent=`${catalog.chapters.length} 卷 · ${episodes.length} 话`;
  let active=catalog.chapters.find(c=>c.id===location.hash.slice(1))||catalog.chapters[0];
  function renderChapter(chapter){
   active=chapter;$('#chapter-number').textContent=`第${chapter.number}卷`;$('#chapter-title').textContent=chapter.title;$('#chapter-description').textContent=chapter.description;$('#chapter-total').textContent=`${chapter.episodes.length} 话 · ${chapter.episodes.reduce((sum,e)=>sum+e.pages,0)} 页`;
   document.querySelectorAll('.chapter-nav-link').forEach(a=>{const selected=a.dataset.chapter===chapter.id;a.classList.toggle('active',selected);if(selected)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current')});
   const grid=$('#episode-grid');grid.replaceChildren();
   for(const episode of chapter.episodes){
    const progress=saved[episode.id];const page=pageNumber(progress?.page,episode.pages);const card=el('article','episode-card');const cover=link('',readerURL(episode,page),'cover-link');cover.setAttribute('aria-label',`阅读第${episode.id}话 ${episode.title}`);
    const img=el('img');img.src=imageURL(episode,1);img.alt=`《${episode.title}》漫画首页`;img.width=1024;img.height=1536;cover.append(img,el('span','episode-badge',`第 ${episode.id} 话`));const bottom=el('span','cover-bottom');bottom.append(el('span','',`${episode.pages} 页`),el('span','',progress?`读到第 ${page} 页`:'开始阅读 ↗'));cover.append(bottom);
    const copy=el('div','card-copy');copy.append(el('div','card-number',episode.version),el('h3','',episode.title),el('p','',episode.summary));const actions=el('div','card-actions');actions.append(link(progress?'继续阅读 →':'开始阅读 →',readerURL(episode,page)));copy.append(actions);card.append(cover,copy);grid.append(card);
   }
  }
  for(const chapter of catalog.chapters){const a=link('',`#${chapter.id}`,'chapter-nav-link');a.dataset.chapter=chapter.id;a.append(el('small','',`第${chapter.number}卷`),el('strong','',chapter.title));$('#chapter-nav').append(a)}
  addEventListener('hashchange',()=>renderChapter(catalog.chapters.find(c=>c.id===location.hash.slice(1))||active));renderChapter(active);
  const last=episodes.filter(e=>saved[e.id]?.updatedAt).sort((a,b)=>saved[b.id].updatedAt-saved[a.id].updatedAt)[0];
  if(last){const page=pageNumber(saved[last.id].page,last.pages);$('#resume').textContent=`继续阅读 · 第${last.id}话 ↗`;$('#resume').href=readerURL(last,page);$('#resume-caption').textContent=`${last.title} · 上次读到第 ${page} / ${last.pages} 页`}
 }else{
  const id=new URLSearchParams(location.search).get('episode');const episode=episodes.find(e=>e.id===id);
  if(!episode){$('#reading-pages').append(el('p','','没有找到这一话，请返回卷章目录选择。'));$('#reader-end').hidden=true;$('#page-select').disabled=true;return}
  document.title=`${episode.title} · 第${episode.id}话 | 逸剑风云决`;
  $('#reader-title').textContent=`${episode.id} · ${episode.title}`;$('#end-title').textContent=episode.title;$('#chapter-label').textContent=`第${episode.chapter.number}卷 · ${episode.chapter.title}`;
  const back=`index.html#${episode.chapter.id}`;$('#back').href=back;$('#end-back').href=back;
  const index=episodes.findIndex(e=>e.id===id);
  for(const [name,other] of [['previous',episodes[index-1]],['next',episodes[index+1]]])if(other){for(const suffix of ['', '-top']){const a=$(`#${name}${suffix}`);a.hidden=false;a.href=readerURL(other);a.textContent=name==='next'?`下一话：${other.title} →`:`← 上一话：${other.title}`}}
  for(let p=1;p<=episode.pages;p++){
   const option=el('option','',`第 ${p} / ${episode.pages} 页`);option.value=p;$('#page-select').append(option);
   const section=el('section','comic-page');section.id=`page-${p}`;section.dataset.page=p;const label=el('div','page-line');label.append(el('span','',`${String(p).padStart(2,'0')} / ${String(episode.pages).padStart(2,'0')}`));const full=link('查看原图 ↗',imageURL(episode,p));full.target='_blank';full.rel='noopener';label.append(full);
   const img=el('img');img.src=imageURL(episode,p);img.alt=`第${episode.id}话《${episode.title}》第${p}页`;img.width=1024;img.height=1536;img.loading=p===1?'eager':'lazy';section.append(label,img);$('#reading-pages').append(section);
  }
  let current=1,ready=false,frame=0,seeking=null;
  function persist(){const all=readSaved();all[id]={page:current,updatedAt:Date.now()};localStorage.setItem(PROGRESS_KEY,JSON.stringify(all))}
  function update(){frame=0;if(!ready)return;if(seeking!==null){const target=document.getElementById(`page-${seeking}`);const expected=parseFloat(getComputedStyle(target).scrollMarginTop)||0;if(Math.abs(target.getBoundingClientRect().top-expected)>12)return;seeking=null}let page=1;document.querySelectorAll('.comic-page').forEach(p=>{if(p.getBoundingClientRect().top<innerHeight*.4)page=Number(p.dataset.page)});if(current!==page){current=page;persist()}if(document.activeElement!==$('#page-select'))$('#page-select').value=current;$('#reading-progress').style.width=`${current/episode.pages*100}%`}
  function gotoPage(value){const requested=pageNumber(value,episode.pages);current=requested;seeking=requested;$('#page-select').value=requested;persist();document.getElementById(`page-${requested}`).scrollIntoView({block:'start',behavior:'instant'});ready=true;update()}
  function selectPage(value){const page=pageNumber(value,episode.pages);history.replaceState(null,'',`#page-${page}`);gotoPage(page)}
  $('#page-select').addEventListener('change',e=>selectPage(e.target.value));addEventListener('hashchange',()=>gotoPage(location.hash.replace('#page-','')));addEventListener('scroll',()=>{if(!frame)frame=requestAnimationFrame(update)},{passive:true});addEventListener('resize',update);
  $('#theme-toggle').addEventListener('click',e=>{const dark=document.body.classList.toggle('dark');e.target.textContent=dark?'日读':'夜读';localStorage.setItem('yijian.theme',dark?'dark':'light')});if(localStorage.getItem('yijian.theme')==='dark'){document.body.classList.add('dark');$('#theme-toggle').textContent='日读'}
  addEventListener('keydown',e=>{if(['SELECT','INPUT','TEXTAREA','BUTTON'].includes(document.activeElement.tagName))return;if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();selectPage(Math.max(1,Math.min(episode.pages,current+(e.key==='ArrowRight'?1:-1))))}});
  requestAnimationFrame(()=>gotoPage(location.hash.replace('#page-','')));
 }
}
// One UI initialization boundary: display failure and preserve the original error in console.
main().catch(error=>{const message=$('#error');message.hidden=false;message.textContent='页面加载失败，请刷新重试。';console.error(error)});

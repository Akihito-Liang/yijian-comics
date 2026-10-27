"""Package generated comic pages without modifying their pixels."""
from pathlib import Path
import importlib.util
import json
import shutil
import zipfile
from html import escape

ROOT=Path(__file__).resolve().parent
SHARED=ROOT.parents[1]/'revision-v3/build.py'
module_spec=importlib.util.spec_from_file_location('comic_style',SHARED)
style=importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(style)

def build():
    pages=json.loads((ROOT/'production.json').read_text())
    selected=json.loads((ROOT/'selected-images.json').read_text())
    assert len(pages)==len(selected)==10
    for spec,item in zip(pages,selected):
        assert spec['page']==item['page']
        name=f"page-{spec['page']:02}.png"
        shutil.copy2(item['source'],ROOT/'assets'/name)
        spec.update(final_image=f'assets/{name}',generation_source=item['source'],actual_panel_count=item['count'])
    (ROOT/'production.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2)+'\n')
    total=sum(p['actual_panel_count'] for p in pages)
    options=''.join(f'<option value="{p["page"]}">第 {p["page"]} 页</option>' for p in pages)
    body=f'''<div class="progress"></div><nav class="bar"><a class="brand" href="../../revision-v3/index.html">逸剑风云决</a><div class="tools"><select id="jump" aria-label="跳转页码">{options}</select><button id="width" class="width">宽屏</button><button id="theme">夜读</button></div></nav>
<header><div class="eyebrow">第一卷 · 第003话 / 重构版</div><h1>药香与木剑</h1><p class="lead">眼睛已经看清，身子却还慢了一步。<br>一把木剑，让少年学会先站稳，也学会与身旁的人配合。</p><div class="meta">10 页 · {total} 格 · 全彩漫画 · 从左到右，自上而下</div><div class="links"><a href="#page-1">开始阅读 ↓</a><a href="episode-003-reconstruction-v4.cbz" download>下载本话 CBZ</a><a href="../../revision-v3/episode-02/index.html">← 第二话</a><a href="../../revision-v3/episode-03/index.html">查看旧版</a></div></header><main class="pages">'''
    for p in pages:
        n=p['page'];img=p['final_image'];loading='eager' if n==1 else 'lazy'
        body+=f'''<section class="page" id="page-{n}" data-page="{n}"><div class="label"><span>{n:02} / 10 · {escape(p['title'])} · {p['actual_panel_count']} 格</span><span><a class="prompt" href="prompts/page-{n:02}.txt">本页分镜</a><a href="{img}" target="_blank" rel="noopener">查看大图 ↗</a></span></div><figure class="frame"><img src="{img}" width="1024" height="1536" loading="{loading}" alt="第三话重构第{n}页：{escape(p['title'])}"></figure></section>'''
    body+='''</main><footer class="end"><h2>药香与木剑</h2><p class="lead">“眼睛看明白了，身子还没学会。”</p><div class="links"><a href="#page-1">回到第一页 ↑</a><a href="episode-003-reconstruction-v4.cbz" download>下载十页漫画包</a><a href="user-storyboard.txt">本次重构原稿</a><a href="production.json">分镜与绘图提示词</a></div><p class="small">按本次用户提供的十页分镜制作。宇文逸沿用已确认的圆润下巴；猴子、木剑归属与人物病后状态贯穿全话。<br>宇文逸、江吟风依据官方Steam立绘；江小彤依据梧桐村时期原作游戏截图。<br>《逸剑风云决》同人漫画改编 · 内置 ImageGen 制作 · <a href="revision-notes.txt">制作与参考记录</a></p></footer>'''
    js='''const jump=document.querySelector('#jump'),pages=[...document.querySelectorAll('.page')];
jump.addEventListener('change',()=>{location.hash='page-'+jump.value});
document.querySelector('#theme').addEventListener('click',e=>{const on=document.body.classList.toggle('dark');e.target.textContent=on?'日读':'夜读'});
document.querySelector('#width').addEventListener('click',e=>{const on=document.body.classList.toggle('wide');e.target.textContent=on?'标准宽度':'宽屏'});
function sync(){let n=1;for(const p of pages){if(p.getBoundingClientRect().top<innerHeight*.4)n=Number(p.dataset.page)}if(document.activeElement!==jump)jump.value=n;const span=document.documentElement.scrollHeight-innerHeight;document.querySelector('.progress').style.width=(span>0?Math.min(100,scrollY/span*100):100)+'%'}
addEventListener('scroll',sync,{passive:true});addEventListener('resize',sync);sync();
addEventListener('keydown',e=>{if(['SELECT','INPUT','TEXTAREA'].includes(document.activeElement.tagName))return;if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();location.hash='page-'+Math.max(1,Math.min(pages.length,Number(jump.value)+(e.key==='ArrowRight'?1:-1)))}});'''
    (ROOT/'index.html').write_text(style.document('药香与木剑 · 第003话重构版',body,js))
    with zipfile.ZipFile(ROOT/'episode-003-reconstruction-v4.cbz','w',compression=zipfile.ZIP_STORED) as z:
        for p in pages: z.write(ROOT/p['final_image'],f"{p['page']:03}.png")
    print(json.dumps({'pages':len(pages),'panels':total,'reader':str(ROOT/'index.html')},ensure_ascii=False))

if __name__=='__main__': build()

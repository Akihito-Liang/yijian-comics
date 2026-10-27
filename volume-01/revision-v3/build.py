"""Package approved raster pages and build a local comic reader; no image editing."""
from pathlib import Path
import json
import shutil
import zipfile
from html import escape

ROOT = Path(__file__).resolve().parent
WORK = ROOT.parents[1]
TITLES = {1: '葬龙谷的风', 2: '梧桐梦醒', 3: '药香与木剑'}
NOTES = {
    1: '刀势压下来，少年第一次知道，握住剑与挡住刀之间还有多远。',
    2: '伸手撑床、失衡、接扶。活下来的人，仍要学着承受疼痛与失去。',
    3: '追赶、失足、观察、配合。一把木剑，也有落下时的重量。',
}
ORIGINALS = {1: '../../episode-01/expanded-v2', 2: '../../episode-02', 3: '../../episode-03'}
CSS = '''
:root{--bg:#ede9df;--paper:#faf7ef;--ink:#26342f;--muted:#777569;--line:#d1cabc;--accent:#903b30}*{box-sizing:border-box}html{scroll-padding-top:86px}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.65 "PingFang SC","Microsoft Yahei",sans-serif}a{color:inherit;text-underline-offset:4px}button,select{font:inherit;color:var(--ink);background:var(--paper);border:1px solid var(--line);border-radius:5px;padding:7px 10px;cursor:pointer}button:hover,a:hover{color:var(--accent)}.bar{position:sticky;top:0;z-index:10;background:var(--bg);border-bottom:1px solid var(--line);padding:12px 24px;display:flex;align-items:center;gap:15px;flex-wrap:wrap}.brand{font-family:"Songti SC",serif;letter-spacing:2px;text-decoration:none;font-size:19px}.tools{display:flex;gap:8px;margin-left:auto}.eyebrow{font-size:11px;letter-spacing:3px;color:var(--accent)}header{max-width:1000px;margin:52px auto 35px;padding:0 24px}h1,h2{font-family:"Songti SC",serif;font-weight:600;letter-spacing:3px}h1{font-size:clamp(34px,5vw,54px);line-height:1.2;margin:16px 0}h2{font-size:28px}.lead{max-width:650px;color:var(--muted);line-height:1.9}.meta{font-size:12px;letter-spacing:1px;color:var(--muted);margin-top:22px}.links{display:flex;gap:20px;flex-wrap:wrap;margin-top:24px;font-size:13px}.pages{max-width:1048px;margin:auto;padding:0 12px}.page{margin-bottom:42px}.label{display:flex;align-items:center;justify-content:space-between;padding:10px 4px;font-size:12px;color:var(--muted)}.label a{margin-left:16px}.frames{display:grid;grid-template-columns:1fr;gap:16px}.frame{margin:0;min-width:0}.frame figcaption{font-size:11px;color:var(--muted);padding:0 0 8px;letter-spacing:2px}.frame img{display:block;width:100%;height:auto;background:var(--paper);box-shadow:0 5px 24px #25312518}.old{display:none}body[data-mode=old] .new{display:none}body[data-mode=old] .old{display:block}body[data-mode=compare] .old{display:block}body[data-mode=compare] .frames{grid-template-columns:1fr 1fr}body[data-mode=compare] .pages{max-width:1720px}body.wide .pages{max-width:1400px}body.dark{--bg:#19211e;--paper:#25302b;--ink:#e5e3d8;--muted:#a9afa2;--line:#3e4941;--accent:#d8a174}.end{border-top:1px solid var(--line);max-width:1000px;margin:40px auto;padding:25px 24px 50px}.small{color:var(--muted);font-size:12px;line-height:1.9}.cards{max-width:1100px;margin:35px auto;display:grid;grid-template-columns:repeat(3,1fr);gap:26px;padding:0 24px}.card{border-top:1px solid var(--line);padding-top:20px}.cover{display:block;overflow:hidden;aspect-ratio:2/3;background:var(--paper)}.cover img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .3s}.cover:hover img{transform:scale(1.015)}.card h2{margin-bottom:5px}.card p{font-size:13px;color:var(--muted);min-height:64px}.card .links{margin-top:14px}.feature{max-width:1052px;margin:50px auto;border-top:1px solid var(--line);padding:22px 0}.feature ul{padding-left:20px;line-height:2.2}.footer-note{max-width:1052px;margin:40px auto;padding:0 24px}.progress{height:2px;background:var(--accent);position:fixed;top:0;left:0;z-index:20;width:0}
@media(max-width:720px){.bar{padding:9px 12px;gap:8px}.brand{font-size:16px}.tools{gap:4px}button,select{font-size:12px;padding:7px}.width{display:none}header{margin-top:32px;padding:0 18px}.cards{grid-template-columns:1fr;max-width:560px}.card p{min-height:0}.pages{padding:0 5px}.label{padding:10px 7px}.label .prompt{display:none}body[data-mode=compare] .frames{grid-template-columns:1fr}.feature{margin:40px 24px}.frame figcaption{padding-left:7px}.links{gap:15px}}
@media print{.bar,header,.label,figcaption,.end,.old,.progress{display:none!important}.pages{padding:0;max-width:none}.page{margin:0;break-after:page}.frames{display:block!important}.frame img{width:100%;box-shadow:none}body{background:white}}
'''
JS = '''
const jump=document.querySelector('#jump'),pages=[...document.querySelectorAll('.page')];
jump.addEventListener('change',()=>{location.hash='page-'+jump.value});
document.querySelector('#mode').addEventListener('change',e=>{document.body.dataset.mode=e.target.value;document.querySelector('#page-'+jump.value).scrollIntoView()});
document.querySelector('#theme').addEventListener('click',e=>{const on=document.body.classList.toggle('dark');e.target.textContent=on?'日读':'夜读'});
document.querySelector('#width').addEventListener('click',e=>{const on=document.body.classList.toggle('wide');e.target.textContent=on?'标准宽度':'宽屏'});
function sync(){let n=1;for(const p of pages){if(p.getBoundingClientRect().top<innerHeight*.4)n=Number(p.dataset.page)}if(document.activeElement!==jump)jump.value=n;const span=document.documentElement.scrollHeight-innerHeight;document.querySelector('.progress').style.width=(span>0?Math.min(100,scrollY/span*100):100)+'%'}
addEventListener('scroll',sync,{passive:true});addEventListener('resize',sync);sync();
addEventListener('keydown',e=>{if(['SELECT','INPUT','TEXTAREA'].includes(document.activeElement.tagName))return;if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();location.hash='page-'+Math.max(1,Math.min(pages.length,Number(jump.value)+(e.key==='ArrowRight'?1:-1)))}});
'''

def document(title, body, script=''):
    return '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+escape(title)+'</title><style>'+CSS+'</style></head><body data-mode="new">'+body+('<script>'+script+'</script>' if script else '')+'</body></html>'

def run():
    manifest=json.loads((ROOT/'selected-images.json').read_text())
    all_pages=[]
    summaries=[]
    for episode,title in TITLES.items():
        folder=ROOT/f'episode-{episode:02}'
        assets=folder/'assets'
        assets.mkdir(exist_ok=True)
        selected=[p for p in manifest if p['episode']==episode]
        selected.sort(key=lambda p:p['page'])
        production=json.loads((folder/'production.json').read_text())
        for item,spec in zip(selected,production):
            assert item['page']==spec['page']
            dst=assets/f"page-{item['page']:02}.png"
            shutil.copy2(item['source'],dst)
            spec.update(actual_panel_count=item['actual_panel_count'],final_image=f'assets/{dst.name}',generation_source=item['source'])
            all_pages.append((episode,item['page'],dst))
        (folder/'production.json').write_text(json.dumps(production,ensure_ascii=False,indent=2)+'\n')
        count=sum(p['actual_panel_count'] for p in selected)
        summaries.append((episode,title,len(selected),count))
        options=''.join(f'<option value="{p["page"]}">第 {p["page"]} 页</option>' for p in selected)
        body=f'<div class="progress"></div><nav class="bar"><a class="brand" href="../index.html">逸剑风云决</a><div class="tools"><select id="jump" aria-label="跳转页码">{options}</select><select id="mode" aria-label="阅读版本"><option value="new">新版</option><option value="compare">新旧对照</option><option value="old">旧版</option></select><button id="width" class="width">宽屏</button><button id="theme">夜读</button></div></nav>'
        body+=f'<header><div class="eyebrow">第一卷 · 第{episode:03}话 / 动作重绘版</div><h1>{title}</h1><p class="lead">{NOTES[episode]}</p><div class="meta">{len(selected)} 页 · {count} 格 · 从左到右，自上而下</div><div class="links"><a href="../index.html">三话目录</a><a href="episode-{episode:03}-v3.cbz" download>下载本话 CBZ</a><a href="production.json">分镜与提示词</a></div></header><main class="pages">'
        for item in selected:
            page=item['page']; image=f'assets/page-{page:02}.png'; old=f'{ORIGINALS[episode]}/assets/page-{page:02}.png'
            loading='eager' if page==1 else 'lazy'
            body+=f'<section class="page" id="page-{page}" data-page="{page}"><div class="label"><span>{page:02} / {len(selected):02} · {item["actual_panel_count"]} 格</span><span><a class="prompt" href="prompts/page-{page:02}.txt">本页分镜</a><a href="{image}" target="_blank" rel="noopener">查看大图 ↗</a></span></div><div class="frames"><figure class="frame new"><figcaption>动作重绘版</figcaption><img src="{image}" width="1024" height="1536" loading="{loading}" alt="第{episode}话《{title}》重绘第{page}页"></figure><figure class="frame old"><figcaption>原版对照</figcaption><img src="{old}" width="1024" height="1536" loading="lazy" alt="第{episode}话原版第{page}页"></figure></div></section>'
        body+='</main><footer class="end"><div class="links"><a href="#page-1">回到第一页 ↑</a>'
        if episode<3: body+=f'<a href="../episode-{episode+1:02}/index.html">下一话：{TITLES[episode+1]} →</a>'
        if episode>1: body+=f'<a href="../episode-{episode-1:02}/index.html">← 上一话</a>'
        body+='<a href="../index.html">三话目录</a></div><p class="small">《逸剑风云决》同人漫画改编 · 内置 ImageGen 绘制。人物参考来源及本版修订记录见目录。<br>旧稿完整保留，可用顶部“新旧对照”查看。</p></footer>'
        (folder/'index.html').write_text(document(f'{title} · 动作重绘版',body,JS))
        with zipfile.ZipFile(folder/f'episode-{episode:03}-v3.cbz','w',compression=zipfile.ZIP_STORED) as z:
            for item in selected: z.write(assets/f"page-{item['page']:02}.png",f"{item['page']:03}.png")
    with zipfile.ZipFile(ROOT/'episodes-001-003-v3.cbz','w',compression=zipfile.ZIP_STORED) as z:
        for episode,page,path in all_pages: z.write(path,f'{episode:03}-{page:03}.png')
    body='<nav class="bar"><a class="brand" href="index.html">逸剑风云决</a><span class="eyebrow">少年武侠彩色漫画</span></nav><header><div class="eyebrow">第一卷 / 第001—003话</div><h1>剑有重量，<br>少年有来路。</h1><p class="lead">从葬龙谷的第一次格挡，到梧桐村的一次接扶，再到树林里接住一把木剑。重绘这三段路上的动作、反应与心绪。</p><div class="meta">三话 · 24 页 · 全彩动作重绘版</div><div class="links"><a href="episode-01/index.html">从第一话开始 →</a><a href="episodes-001-003-v3.cbz" download>下载三话合集 CBZ</a></div></header><main><div class="cards">'
    for episode,title,pages,count in summaries:
        body+=f'<article class="card"><a class="cover" href="episode-{episode:02}/index.html"><img src="episode-{episode:02}/assets/page-01.png" width="1024" height="1536" alt="{title}首页"></a><div class="meta">第{episode:03}话 · {pages} 页 · {count} 格</div><h2>{title}</h2><p>{NOTES[episode]}</p><div class="links"><a href="episode-{episode:02}/index.html">开始阅读 →</a><a href="episode-{episode:02}/episode-{episode:03}-v3.cbz" download>下载</a></div></article>'
    body+='</div><section class="feature"><div class="eyebrow">看看动作的变化</div><ul><li><a href="episode-01/index.html#page-5">第一话 · 第 5 页：蓄势、硬挡、被压低，再由老镖师卸开刀锋。</a></li><li><a href="episode-02/index.html#page-4">第二话 · 第 4 页：颤抖、前倾、接扶，病后的动作仍有重量。</a></li><li><a href="episode-03/index.html#page-5">第三话 · 第 5 页：拨中、旋转脱手、屈膝接剑，合作分成可读的瞬间。</a></li></ul><p class="small">阅读页顶部可切换“新版 / 新旧对照 / 旧版”。方向键可翻页。</p></section></main><footer class="footer-note"><p class="small">常规约 25—35 格；重要大战可加长。本版第一话保留 12 页的加长篇幅，第二、三话各 6 页。<br>人物以原作参考为依据。陈武、方阔海的立绘尚未核验，按用户确认使用远景、剪影与手部镜头，待取得原图后补正面。</p><div class="links"><a href="revision-notes.txt">修订与参考来源</a><a href="selected-images.json">成稿清单</a></div><p class="small">《逸剑风云决》同人漫画改编 · ImageGen 制作 · 本地试读稿</p></footer>'
    (ROOT/'index.html').write_text(document('逸剑风云决 · 三话动作重绘版',body))
    print(json.dumps({'pages':len(all_pages),'episodes':summaries,'reader':str(ROOT/'index.html')},ensure_ascii=False))

if __name__=='__main__':
    run()

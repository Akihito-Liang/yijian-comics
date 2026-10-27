"""Build the six-page reader and CBZ from original ImageGen PNGs."""
import html
import json
import shutil
import struct
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parent
episode = json.loads((root / 'production.json').read_text())
manifest = json.loads((root / 'image-manifest.json').read_text())
titles = [p['title'] for p in episode['pages']]
for page, item in zip(episode['pages'], manifest['pages']):
    shutil.copy2(item['source'], root / item['file'])
    with (root / item['file']).open('rb') as f:
        header = f.read(24)
    assert header[:8] == b'\x89PNG\r\n\x1a\n'
    width, height = struct.unpack('>II', header[16:24])
    assert width * 3 == height * 2, (width, height)
    assert len(page['panels']) == 5
    page['dimensions'] = [width, height]
    page['generation_source'] = item['source']
    page['correction_prompt'] = item['correction_prompt']
    page['prompt_file'] = f"prompts/page-{page['number']:02}.txt"
    (root / page['prompt_file']).write_text(page['prompt'])
episode['status'] = 'complete_trial_edition'
episode['generation_tool'] = 'built-in image_gen'
episode['verification'] = '逐页目视核对五格、对白、人物与木剑归属；修正猴子比例、木剑握持和短柄造型、对白气泡归属及接剑站位。第六页经用户授权补写。'
(root / 'episode.json').write_text(json.dumps(episode, ensure_ascii=False, indent=2) + '\n')
(root / 'image-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')

template = (root.parent / 'episode-01/reader-v1.html').read_text()
template = template.replace('葬龙谷的风 · 第一卷第一集', '药香与木剑 · 第三话')
start, end = template.index('<header>'), template.index('</header>') + len('</header>')
template = template[:start] + '''<header><div class="eyebrow">第一卷 · 初入江湖 / 第003话</div><h1>药香与木剑</h1><p class="intro">一把木剑，被顽皮的猴子带上了树。<br>追不上时，少年开始认真看清脚下的路。</p><div class="meta"><span>全彩试读版</span><span>6 页 · 30 格</span><span>从左到右，自上而下</span></div></header>''' + template[end:]
sections = []
for p, title in zip(episode['pages'], titles):
    n = p['number']
    lines = []
    for i, panel in enumerate(p['panels'], 1):
        text = '<br>'.join(html.escape(t['speaker'] + '：' + t['line']) for t in panel['text'])
        if not text:
            text = '（无对白）'
        lines.append(f'<p><b>{i:02}</b><span>{text}</span></p>')
    loading = 'eager' if n == 1 else 'lazy'
    sections.append(f'''<section class="page" id="page-{n}" data-page="{n}" aria-label="第{n}页 {title}"><div class="page-label"><span>{n:02} / 06</span><span>{title}</span><a href="{p['file']}" target="_blank" rel="noopener">查看原图 ↗</a></div><img src="{p['file']}" width="1024" height="1536" alt="第{n}页：{title}。对白见下方逐格文字。" loading="{loading}"><details class="transcript"><summary>本页逐格文字</summary>{''.join(lines)}</details></section>''')
start, end = template.index('<main>'), template.index('</main>') + len('</main>')
template = template[:start] + '<main>' + '\n'.join(sections) + '</main>' + template[end:]
start, end = template.index('<footer'), template.index('</footer>') + len('</footer>')
template = template[:start] + '''<footer class="end"><div class="downloads"><a href="药香与木剑-第003话.cbz" download>下载六页漫画包（CBZ）</a><a href="#page-1">回到第一页 ↑</a><a href="episode.json" download>分镜与绘图提示词</a><a href="../episode-02/index.html">阅读第二话</a></div><p class="credits">《逸剑风云决》同人漫画改编。人物依据原作参考。第1—5页按用户分镜制作，第6页经用户授权补写。<br>宇文逸、江吟风参考官方 Steam 人物介绍；江小彤参考梧桐村时期原版游戏截图。<br>使用内置 ImageGen 制作。</p></footer>''' + template[end:]
template = template.replace('scroll-behavior:smooth', 'scroll-behavior:auto')
template = template.replace('.scrollIntoView()', ".scrollIntoView({behavior:'instant',block:'start'})")
(root / 'index.html').write_text(template)
with zipfile.ZipFile(root / '药香与木剑-第003话.cbz', 'w', zipfile.ZIP_DEFLATED) as archive:
    for p in episode['pages']:
        archive.write(root / p['file'], f"{p['number']:02}.png")
    archive.writestr('ComicInfo.xml', '<?xml version="1.0" encoding="utf-8"?><ComicInfo><Title>药香与木剑</Title><Series>逸剑风云决·同人漫画</Series><Number>3</Number><PageCount>6</PageCount><LanguageISO>zh</LanguageISO></ComicInfo>')
with zipfile.ZipFile(root / '药香与木剑-第003话.cbz') as archive:
    assert archive.testzip() is None
    assert len([n for n in archive.namelist() if n.endswith('.png')]) == 6
print('完成：6页、30格，6张1024×1536 PNG、阅读页和CBZ归档。')

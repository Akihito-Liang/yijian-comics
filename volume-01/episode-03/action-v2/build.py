import json
import shutil
import struct
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parent
original = root.parent
revision = json.loads((root / 'revision.json').read_text())
episode = json.loads((original / 'episode.json').read_text())
for page in episode['pages']:
    n = page['number']
    source = Path(revision['sources'].get(str(n), str(original / page['file'])))
    destination = root / page['file']
    shutil.copy2(source, destination)
    width, height = struct.unpack('>II', destination.read_bytes()[16:24])
    assert (width, height) == (1024, 1536)
    page['generation_source'] = str(source)
    if n in revision['revised_pages']:
        page['prompt'] = (root / f'prompts/page-{n:02}.txt').read_text()
        page['correction_prompt'] = (root / 'prompts/page-05-correction.txt').read_text() if n == 5 else None
episode['revision'] = '动作强化版：第2、3、5页重绘'
episode['verification'] = '逐页目视核对五格、对白、人物服装、木剑归属与动作衔接。'
(root / 'episode.json').write_text(json.dumps(episode, ensure_ascii=False, indent=2))
reader = (original / 'index.html').read_text()
reader = reader.replace('<title>药香与木剑 · 第三话</title>', '<title>药香与木剑 · 动作强化版</title>')
reader = reader.replace('<span>全彩试读版</span>', '<span>动作强化版 · 第2、3、5页重绘</span>')
reader = reader.replace('</header>', '<p><a href="compare.html" style="color:var(--accent)">原版 / 新版并排对比 →</a></p></header>')
reader = reader.replace('href="../episode-02/index.html"', 'href="../../episode-02/index.html"')
reader = reader.replace('药香与木剑-第003话.cbz', '药香与木剑-第003话-动作强化版.cbz')
for n in revision['revised_pages']:
    marker = f'<a href="assets/page-{n:02}.png"'
    reader = reader.replace(marker, f'<button class="version" data-n="{n}" aria-pressed="false">切换看原版</button>' + marker)
reader = reader.replace('</script>', '''document.querySelectorAll('.version').forEach(button=>button.addEventListener('click',()=>{
const old=button.getAttribute('aria-pressed')!=='true', n=button.dataset.n.padStart(2,'0');
button.closest('.page').querySelector('img').src=(old?'../':'')+'assets/page-'+n+'.png';
button.setAttribute('aria-pressed',String(old));button.textContent=old?'切回动作强化版':'切换看原版';
}));</script>''')
(root / 'index.html').write_text(reader)
with zipfile.ZipFile(root / '药香与木剑-第003话-动作强化版.cbz', 'w', zipfile.ZIP_DEFLATED) as archive:
    for page in episode['pages']:
        archive.write(root / page['file'], f"{page['number']:02}.png")
    archive.writestr('ComicInfo.xml', '<ComicInfo><Title>药香与木剑·动作强化版</Title><Number>3</Number><PageCount>6</PageCount><LanguageISO>zh</LanguageISO></ComicInfo>')
with zipfile.ZipFile(root / '药香与木剑-第003话-动作强化版.cbz') as archive:
    assert archive.testzip() is None
    assert len([n for n in archive.namelist() if n.endswith('.png')]) == 6
old_reader = (original / 'index.html').read_text()
if 'action-v2/compare.html' not in old_reader:
    old_reader = old_reader.replace('</header>', '<p><a style="color:var(--accent)" href="action-v2/compare.html">动作强化版已完成：查看第2、3、5页对比 →</a></p></header>')
    (original / 'index.html').write_text(old_reader)
print('已生成六页30格动作强化版、可切换阅读页、CBZ；原版保留。')

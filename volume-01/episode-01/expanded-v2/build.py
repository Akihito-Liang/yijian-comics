"""Assemble the expanded reader and copy original generated PNGs without processing."""
import copy
import html
import json
import shutil
from pathlib import Path

root = Path(__file__).resolve().parent
parent = root.parent
original = json.loads((parent / 'episode.json').read_text())
drafts = {p['number']: p for p in json.loads((root / 'new-pages.json').read_text())}
manifest = json.loads((root / 'image-manifest.json').read_text())
(root / 'assets').mkdir(exist_ok=True)
episode = copy.deepcopy(original)
episode['edition'] = '十二页扩展版 · 02'
episode['pages'] = []
episode['revision_notes'] = '加入镖队日常、退路受阻、近身接战、寒毒感受、伤亡反应、逼问解药与南行梦魇。延续游戏开场顺序，新增对白与过场为同人创作。'
for item in manifest:
    number = item['number']
    if item['type'] == 'new':
        page = copy.deepcopy(drafts[number])
        page.pop('refs', None)
    else:
        page = copy.deepcopy(original['pages'][item['originalPage'] - 1])
        page['original_page'] = item['originalPage']
        page['original_prompt'] = page.pop('prompt')
        page['prompt'] = item.get('editPrompt', page['original_prompt'])
    page['number'] = number
    page['file'] = f'assets/page-{number:02}.png'
    page['generation_source'] = item['source']
    if item.get('correctionPrompt'):
        page['correction_prompt'] = item['correctionPrompt']
    # The rendered ninth page splits the two reactions into separate panels.
    if number == 9:
        page['beats'][3:4] = ['帮众：陈头领……山上的弟兄还没撤！', '陈武：闭嘴。']
    page['panel_count'] = len(page['beats'])
    shutil.copy2(item['source'], root / page['file'])
    episode['pages'].append(page)
episode['panel_count'] = sum(p['panel_count'] for p in episode['pages'])
(root / 'episode.json').write_text(json.dumps(episode, ensure_ascii=False, indent=2))

backup = parent / 'reader-v1.html'
if not backup.exists():
    shutil.copy2(parent / 'index.html', backup)
template = backup.read_text()
options = ''.join(f'<option value="{n}">第 {n} 页</option>' for n in range(1, 13))
start = template.index('<select id="jump"')
end = template.index('</select>', start) + len('</select>')
template = template[:start] + '<select id="jump" aria-label="跳转页码">' + options + '</select>' + template[end:]
sections = []
for p in episode['pages']:
    n = p['number']
    title = html.escape(p['title'])
    transcript = ''.join(f'<p><b>{i:02}</b><span>' + html.escape(beat).replace('\n', '<br>') + '</span></p>' for i, beat in enumerate(p['beats'], 1))
    loading = 'eager' if n == 1 else 'lazy'
    sections.append(f'''<section class="page" id="page-{n}" data-page="{n}" aria-label="第{n}页 {title}">
<div class="page-label"><span>{n:02} / 12</span><span>{title}</span><a href="{p['file']}" target="_blank" rel="noopener">查看原图 ↗</a></div>
<img src="{p['file']}" width="1024" height="1536" alt="第{n}页：{title}。漫画对白见下方逐格文字。" loading="{loading}">
<details class="transcript"><summary>本页逐格文字</summary>{transcript}</details></section>''')
start = template.index('<main>')
end = template.index('</main>', start) + len('</main>')
template = template[:start] + '<main>' + '\n'.join(sections) + '</main>' + template[end:]
template = template.replace('彩色试读版 01', '彩色扩展版 02').replace('6 页 · 32 格', f'12 页 · {episode["panel_count"]} 格')
template = template.replace('葬龙谷的风 · 第一卷第一集</title>', '葬龙谷的风 · 十二页扩展版</title>')
template = template.replace('下载六页漫画包（CBZ）', '下载十二页漫画包（CBZ）').replace('葬龙谷的风-第一集.cbz', '葬龙谷的风-第一集-十二页扩展版.cbz')
template = template.replace('Math.min(6,Number(jump.value)', 'Math.min(12,Number(jump.value)')
(root / 'index.html').write_text(template)
package = (parent / 'package.py').read_text().replace('six original', 'twelve expanded').replace('葬龙谷的风-第一集.cbz', '葬龙谷的风-第一集-十二页扩展版.cbz')
(root / 'package.py').write_text(package)
print(f'Reader built: {len(episode["pages"])} pages, {episode["panel_count"]} panels')

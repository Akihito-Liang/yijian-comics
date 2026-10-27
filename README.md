# 逸剑风云决 · 少年武侠彩色漫画

《逸剑风云决》同人漫画改编项目，收录漫画成稿、分镜与制作记录，并提供本地漫画书架和 CBZ 下载。

从葬龙谷的一趟镖，到梧桐村的一碗药。少年的江湖，从这里开始。

## 快速阅读

需要 Python 3 和现代浏览器，无需安装前端依赖。

在仓库根目录运行：

```bash
python3 -m http.server 8766 --bind 127.0.0.1
```

然后打开 [本地漫画书架](http://127.0.0.1:8766/)。在 macOS 上，也可以双击根目录的 `start-local.command` 启动；终端按 `Ctrl+C` 停止服务。

书架通过 HTTP 加载 `catalog.json`，请使用上述本地服务访问，不要直接双击 `index.html`。如果端口已被占用，可先确认该地址是否已有漫画服务，或改用其他端口并访问对应地址。

漫画图片和页面均保存在本地，阅读时不需要联网。

## 当前收录

第一卷 **初入江湖**，当前书架共收录 **4 话、40 页**。展示版本以 [catalog.json](catalog.json) 为准，历史版本保留在各话目录中。

| 话数 | 标题 | 页数 | 书架版本 | 下载 |
| --- | --- | ---: | --- | --- |
| 001 | 葬龙谷的风 | 12 | 动作重绘版 | [CBZ](volume-01/revision-v3/episode-01/episode-001-v3.cbz) |
| 002 | 梧桐梦醒 | 6 | 动作重绘版 | [CBZ](volume-01/revision-v3/episode-02/episode-002-v3.cbz) |
| 003 | 药香与木剑 | 10 | 十页重构版 | [CBZ](volume-01/episode-03/reconstruction-v4/episode-003-reconstruction-v4.cbz) |
| 004 | 猎户少年 | 12 | 猎户初识篇 | [CBZ](volume-01/episode-04/episode-004.cbz) |

CBZ 文件可使用支持该格式的漫画阅读器打开。

## 阅读功能

- 按卷浏览，点击小话封面进入阅读。
- 通过页码选择器或左右方向键跳转漫画页。
- 切换日读／夜读模式，查看原图。
- 切换上一话／下一话，下载当前话的 CBZ。
- 自动记录阅读位置，从书架的“继续阅读”入口返回。

阅读进度和夜读设置保存在当前浏览器的本地存储中，不会跨设备同步。更换浏览器、访问端口或清除网站数据后，原有记录可能不可用。

## 目录结构

```text
.
├── index.html                 # 漫画书架首页
├── read.html                  # 通用阅读页
├── catalog.json               # 卷章目录、展示版本与下载路径
├── site.css / site.js         # 书架与阅读器样式、交互
├── start-local.command        # macOS 本地启动脚本
├── references/                # 原作及官方资料参考、来源记录
└── volume-01/
    ├── episode-01/            # 第一话初版与 expanded-v2 扩展版
    ├── episode-02/            # 第二话初版及制作资料
    ├── episode-03/            # 第三话各版本
    │   └── reconstruction-v4/ # 当前十页重构版
    ├── episode-04/            # 第四话成稿及制作资料
    └── revision-v3/           # 第一至第三话的动作重绘版本
```

各版本目录按实际制作情况保存 `assets/` 成稿、`prompts/` 提示词、分镜、修订记录、独立阅读页和 CBZ 文件。部分目录还包含生成阅读页或打包漫画的 Python 脚本；日常阅读无需运行这些脚本。

## 新增或更新小话

1. 将成稿放入对应版本的 `assets/` 目录，按 `page-01.png`、`page-02.png` 等连续命名。
2. 准备对应的 CBZ 文件。
3. 在 `catalog.json` 的 `chapters` 中选择所属卷，向其 `episodes` 添加记录，或更新已有记录。
4. 刷新书架，检查封面、全部漫画页、前后话导航和下载链接。

小话记录示例（路径和标题需替换为实际内容）：

```json
{
  "id": "005",
  "title": "新话标题",
  "summary": "这一话的简短介绍。",
  "pages": 8,
  "version": "初版",
  "base": "volume-01/episode-05/assets/",
  "download": "volume-01/episode-05/episode-005.cbz"
}
```

`id` 应在整个目录中唯一，`base` 以 `/` 结尾；路径均相对于仓库根目录。`pages` 填写实际完成页数，每话不固定页数或格数。书架和前后话导航按 `chapters`、`episodes` 的排列顺序展示。

更新某话的展示版本时，修改 `base`、`download`、`pages` 和 `version` 即可，保留原 `id` 可继续关联该话的阅读记录。

## 制作说明

项目使用 AI 图像生成与局部修稿制作漫画页面，并保留分镜、提示词和修订记录，便于追溯各版本的制作过程。原作参考资料及其来源见 [references/](references/)。本项目为同人改编，非官方作品。

# 烈焰爆破 × 燃油掷弹

Fubgun《流亡黯道 2》古灵军团攻略的中文阅读版，按原文 **0.5.5** 版本整理。

**在线阅读：[GitHub Pages](https://fincerdw.github.io/poe2-flameblast-oil-grenade-guide/)**

![攻略与装备提示预览](docs/preview.png)

## 功能

- 简体／繁体中文切换，术语参考 [流亡2编年史](https://poe2db.tw)。
- 九阶段养成与技能连线，同步展示阶段装备和两组武器。
- 247 份原文游戏提示：悬停查看、点击固定、Esc 关闭，支持手机点按。
- 可展开英文提示原文；相同外观珠宝保留独立词缀。
- 转型清单、剧情奖励勾选、品质计算和术语搜索；阅读设置保存在当前浏览器。
- 使用 [霞鹜新晰黑](https://github.com/lxgw/LxgwNeoXiHei)，字体、游戏图片和提示数据全部内嵌。
- 单个 HTML 可离线阅读，支持打印当前阶段／另存 PDF。

## 本地构建

需要 Python 3.12。构建使用已保存的资料，不需要联网采集。

```sh
python -m pip install -r requirements.txt
python build.py
```

生成 `烈焰爆破-燃油掷弹攻略.html`，可直接用浏览器打开。

构建与部署同名的首页：

```sh
python build.py --output _site/index.html
python -m http.server 8765 --directory _site
```

访问 <http://localhost:8765/>。在线页面保存为 HTML 后也可离线使用，原文／数据库等外部链接仍需网络。

## 项目结构

| 文件／目录 | 用途 |
| --- | --- |
| `build.py` | 整理九阶段内容，转换简繁，内嵌资料并生成单文件 |
| `template.html` | 页面结构、样式和阅读交互 |
| `prepare_tooltips.py` | 编译与翻译实际采集的原文提示 |
| `tooltip-ui.js`、`tooltip-ui.css` | 提示浮层、定位与图标尺寸约束 |
| `research/` | 构建所需的原文快照、术语、提示与素材清单 |
| `assets/game/` | 原攻略使用的游戏素材缓存 |
| `assets/font/` | 霞鹜新晰黑 WOFF2 和字体授权全文 |
| `fetch_assets.py` | 按已保存的素材清单重新下载图片，可选联网维护工具 |
| `.github/workflows/deploy.yml` | 推送 `main` 后自动构建并部署 GitHub Pages |

生成文件、临时分析输出、调试截图与 Python 缓存不提交到仓库；部署仅发布生成的 `index.html`。

## 来源与版本

原攻略：[0.5.5 Fubgun Flameblast Oil Grenade](https://mobalytics.gg/poe-2/builds/fubgun-flameblast-oil-grenade)，原作者 **Fubgun**，页面更新日期为 **2026-09-12**。中文整理日期为 **2026-10-02**。原文九阶段与英文提示均为采集时的快照，后续游戏改版不会自动同步。

本页保留正文与提示各自的版本数据；原文缺失数值不会补猜。天赋逐点连线仍链接原版规划器，PoB 导入码仅对应原文的一个高预算配置。

这是非官方的中文整理项目。攻略、游戏美术及字体的来源、权利归属与授权见 [素材与授权说明](ASSET_NOTICES.md)。

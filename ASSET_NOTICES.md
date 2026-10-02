# 来源与素材说明

## 攻略和数据库

攻略内容及配置来自 [Fubgun 在 Mobalytics 发布的原攻略](https://mobalytics.gg/poe-2/builds/fubgun-flameblast-oil-grenade)。中文页面为翻译与结构整理，保留原作者、原文链接、版本日期和英文提示快照。

中文术语参考 [流亡2编年史 poe2db.tw](https://poe2db.tw)，每个术语的数据库链接保留在页面内。

## 游戏美术

`assets/game/` 中的技能、辅助、物品与昇华图片来自原攻略实际使用的 CDN 素材。路径和来源记录保存在 `research/asset-manifest.json` 与素材清单中。Path of Exile 2 游戏美术及相关知识产权归 **Grinding Gear Games** 所有。

## 字体

字体为 [霞鹜新晰黑 LXGW Neo XiHei](https://github.com/lxgw/LxgwNeoXiHei) **v1.305**。页面内嵌完整 WOFF2 字库；仓库同时保留 [原版授权全文](assets/font/LICENSE.md) 和 [简体中文参考译本](assets/font/LICENSE_CHS.md)。字体遵循 IPA Font License Agreement v1.0。

页面页尾提供授权全文、IPA 原始字体官方入口，以及选择本地 IPA 字体即时替换的功能。WOFF2 为原字体的网页格式转换，未更改字形。

本项目不以统一授权重新许可上述第三方攻略、素材或字体；相应权利与原有授权保持归属原提供方。

## 开源天赋树与配点

地图数据与图集来自 [poe2-tools/poe2-build-planner](https://github.com/poe2-tools/poe2-build-planner)，固定提交 `a173f7b0d398951693fee83ee5ee40f327d4a749` 的 `Skill Trees/0.5.2/`。`research/passive-tree.json` 为该数据的精简快照，保留主树与古灵军团；`assets/passive/` 保存原始节点、边框、佣兵背景图集。

该项目的源代码采用 MIT 许可证。本项目的 Canvas 实现参考其图集索引、连线圆弧与显示层级约定。原始 [MIT 许可证及游戏数据说明](assets/passive/LICENSE-planner.txt) 同时内嵌在生成的 HTML 中；开源源代码许可不改变 Grinding Gear Games 对游戏美术和数据的权利。

九阶段配点来自 Fubgun 原攻略的 `.build` 导出，按共用、武器组 1、武器组 2 保存于 `research/passive-stages.json`。中文节点名称和效果参考编年史的对应公开条目；未直接匹配的说明使用其术语翻译，数值保留地图的 0.5.2 快照。来源与中文说明保存在 `research/passive-translations.json`。

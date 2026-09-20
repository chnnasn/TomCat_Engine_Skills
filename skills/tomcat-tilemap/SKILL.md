---
name: tomcat-tilemap
description: 编辑或排查 TomCat Tilemap2D、Grid 与 Tile Palette，进行网格绘制、填充、擦除、移动及调色板资源配置。用于 2D 关卡瓦片制作。
---

# TomCat Tilemap 与 Palette

## 依据与执行范围

基于 TomCat v0.3.0 / `0a731be`。引擎根目录下
`Editor/TomCatInut/src/panels/SceneHierarchyPanel.cpp` 的 Tile Palette、Tilemap2D Inspector 和 Grid 布局，
以及 `Editor/TomCatInut/src/panels/ContentBrowserPanel.cpp` 的 TilePalette 资源创建是入口。
这是 UI 操作与源码指导 Skill。MCP V1 没有瓦片绘制/填充工具；即便组件出现在 schema 中，也不能推断稀疏格子数据可写。
有 UI 工具时依实际界面实施，没有时提供明确步骤或修改用户授权的项目源码，不声称完成画图。

## 制作流程

- 先确认目标实体有 Tilemap2D，并检查用于显示的 TilemapRenderer2D、网格布局与单元尺寸。Inspector 提供 Rectangle、Isometric、Isometric Z As Y、Hexagon；按当前源码验证坐标转换，不能统一套用矩形坐标公式。
- Project 创建 Tile Palette (`.tctilepalette`)，选择真实 Sprite 子资源并配置 CellSize/CellGap。调色板资源保存与关卡保存分别完成。
- 选中目标 Tilemap2D，使用 Inspector 的 Open Tile Palette 或 Window 对应面板。面板可能正在编辑一个 Palette 资产；先区分资产编辑与目标地图绘制，核对 Active Tilemap。
- 工具包括 Select、Move、Paint、Box、Eyedropper、Erase、Fill。先小区域验证 Cell、Box End、Move To、Tint 和当前 Sprite，再扩大范围；Fill/Box 的范围以实际实现为准，不推定无界填充。
- 需要对已有地图操作时，先检查目标区域和当前选区，防止在错误地图上擦除或移动。Undo 后核对目标格子和未选区域。

## 验证与边界

检查不同位置/负坐标的网格对齐、枢轴和 PPU、颜色、排序及格子移动结果；保存重载并进入 Play 核对渲染。
Sprite 显示不代表已有物理碰撞，不从画出的格子推断碰撞体自动生成；需要碰撞时查当前组件与实现。
修改底层资源时先找当前 TilePalette codec 和 Tilemap 序列化实现，保持 Sprite 身份，不能照搬 Unity Tilemap YAML。
若验收依赖未执行的拖动、选区或视口交互，明确列出该验证缺口。

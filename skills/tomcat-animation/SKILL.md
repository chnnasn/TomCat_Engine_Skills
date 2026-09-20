---
name: tomcat-animation
description: 制作或调试 TomCat Sprite Animation Clip 和 Animator Controller、参数、状态、过渡及动画资源。用于 2D 精灵动画，不用于骨骼动画。
---

# TomCat Sprite Animation

## 依据与能力

基于 TomCat v0.3.0 / `0a731be`。按需读取引擎根目录：
`Editor/TomCatInut/src/panels/SceneHierarchyPanel.cpp`（DrawAnimatorControllerAssetEditor、动画预览和图编辑），
`Editor/TomCatInut/src/panels/ContentBrowserPanel.cpp`（资源创建），
`TomCat/src/TomCat/Scene/SpriteAnimation.h` 和 `TomCat/src/TomCat/Scene/SpriteAnimatorAuthoring.h`（数据与命名规则）。
通过 Editor 界面或基于实际 codec 的源码工作实施。MCP V1 没有 Clip、Controller 或状态图编辑工具；复杂数组/图结构不能假设可用 component_set 写入。

## 工作流

- 在 Project 的创建菜单生成 Animation Clip (`.tcanim`) 和 Animator Controller (`.tccontroller`)。打开 Clip，按预期顺序选择真实 Sprite 子资源，检查帧持续时间、循环与预览，再 Save。
- Controller 设置初始状态、各状态引用的 Clip、参数与过渡。参数类型是 Bool、Int、Float、Trigger；条件必须匹配类型，不能把 Trigger 当成普通持续布尔状态。
- 当前编辑器 Bool/Trigger 条件是 If/If Not，Float 是 Greater/Less，Int 还支持 Equals/Not Equal。使用 AnyState 和 Exit Time 时在 Play 验证触发顺序与时机。
- Window 的 Animation/Animator 工具用于时间线和图编辑。区分正在修改的是实体上的动画配置还是外部 Controller/Clip；资源面板的保存状态与场景保存分别核对。
- 为实体配置 SpriteAnimator 并绑定对应资源。外部 Controller 和 Clip 在 Play 开始时加载，修改后重新进入 Play 验证，不能承诺立即热更新。
- 重命名或删除参数/状态时检查引用它的过渡和条件；基于实际 authoring helper 维护引用，不靠字符串批量替换修改图结构。

## 验证

检查初始状态、每条关键过渡、一次性 Trigger、循环与非循环 Clip、退出时间边界，停止后再 Play 检查默认值复位。
保存并重载资源，确认 Sprite 句柄仍指向预期切片。区分 Clip 预览正确和运行时条件正确。
这是 2D Sprite 动画系统，不把 Mesh 信息或 Sprite 状态机解释为骨骼动画支持。
没有界面执行能力时输出可复现操作步骤；没有运行证据时标注尚未验证。

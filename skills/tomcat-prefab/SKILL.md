---
name: tomcat-prefab
description: 处理 TomCat 关联 Prefab、实例覆盖、逐属性 Apply/Revert、嵌套与变体。用于创建或维护可复用实体模板，以及诊断模板更新冲突。
---

# TomCat Prefab

## 使用范围与依据

基于 TomCat v0.3.0，源码基线 `0a731be`。以下路径相对用户的引擎源码根目录；使用不同版本时先核对实现。
读取 `docs/PREFAB_WORKFLOW.zh-CN.md` 了解合并语义，再读取 `docs/EDITOR_UX_REWORK.md` 和
`Editor/TomCatInut/src/panels/SceneHierarchyPanel.cpp` 中 `Apply property` / `Revert property`。
旧 Prefab 文档所说“尚无逐字段面板”已被后续 Inspector 实现更新。

这是编辑器操作与源码指导 Skill。MCP V1 没有 Prefab 创建、Apply/Revert 或变体工具；不能用 component_set 模拟模板合并。
有可用 UI 操作工具时按实际界面操作，否则提供具体步骤或处理用户授权的源码任务，不声称已执行界面动作。

## 编辑流程

- 从 Project 拖入 `.tcprefab` 创建关联实例。先选中实例根，检查源模板、Overrides 的 Source/Instance 和结构差异，再确定修改范围。
- 共同存在组件的反射属性可用 **Apply property** 写回模板，或 **Revert property** 恢复模板值。实体、组件增删与结构差异用整体 Apply/Revert。
- **Update Prefab (Keep Overrides)** 合并新模板并保留实例覆盖。冲突时读 Console，保留现场并解决具体冲突；不要改 LocalID 伪装成新节点。
- **Apply All Overrides to Prefab** 会修改模板并同步同场景其他关联实例，保留它们自己的覆盖；只要用户要的是本实例修改，就保留覆盖，不擅自 Apply。
- **Revert All Prefab Overrides** 恢复模板内容，根 Transform 和外部父级仍是关卡放置数据。**Unpack Prefab** 解除本层关联并保留内容。
- 把关联子实例放在普通父实体下，再从父实体创建 Prefab，保留嵌套关联。关联实例根可用 **Create Prefab Variant From Selection** 创建变体。

## 验证与边界

用两个实例验证：修改目标实例、检查另一实例覆盖、保存重载，再验证模板更新与根位置保持。嵌套/变体检查依赖链，不允许循环，最大深度 32。
Apply 的 Undo/Redo 同时涉及模板文件和场景；模板被外部修改时可能拒绝撤销，不能强行覆盖。跨文件历史仅在当前场景会话保留。
自动刷新不自动保存关卡。运行时 C# Instantiate 是快照创建，不会自动刷新已经运行的实例。
底层证据：`TomCat/src/TomCat/Scene/Serialization/PrefabLink.inl`、`Tests/PhysicsRegression/src/PrefabRegression.h`。

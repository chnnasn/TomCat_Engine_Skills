---
name: tomcat-assets
description: 处理 TomCat Project 资源检查、导入设置 Apply/Revert 和 Sprite Atlas 切片、枢轴与稳定子资源引用。用于图片资源工作流和图集引用问题。
---

# TomCat Assets 与 Sprite Atlas

## 依据与执行方式

基于 TomCat v0.3.0 / `0a731be`。引擎根目录下的
`Editor/TomCatInut/src/panels/ContentBrowserAssetInspector.inl`、
`Editor/TomCatInut/src/panels/ContentBrowserPanel.cpp` 和 `docs/EDITOR_UX_REWORK.md` 是依据。
这是编辑器操作与源码排查 Skill；MCP V1 没有资源导入、切片或资产保存接口。
有 UI 工具时从实际界面操作，否则给出步骤或基于源码处理明确的开发任务。不要把场景保存当成导入设置 Apply。

## Project 与导入

在 Project 搜索并选中资源，主 Inspector 显示资源信息；选中后面板不变先检查 Inspector 是否锁定。
编辑 Assets 下的资源；Packages 在 Inspector 中只读，需要修改时先确定用户要创建项目副本还是维护引擎包。
导入属性先修改草稿，再 Apply 发布，Revert 放弃草稿。遇到外部修改冲突先重新检查磁盘与草稿，不覆盖未知新内容。
图片可显示真实缩略图；音频/字体/Mesh/Material/Shader 信息不代表提供完整波形、字形、3D 或节点编辑器。

## Sprite Atlas

在适用图片的 Project 右键使用 Sprite Atlas Tools...；菜单可用性取决于所选资源。
检查 Rect、Pivot、Pixels Per Unit、Border 和 Stable ID。修改切片名称应保留 Stable ID，保持引用 AssetHandle 稳定；不要按列表序号重新生成身份。
预览支持缩放和拖动切片，Shift 调整大小、Alt 调整枢轴。自动切片/打包前检查已有 Sprite 被动画、Tilemap 或实体引用的情况，再审阅结果并应用。
按实际界面字段选择透明区域或网格切片、打包及 TGA 导出，不猜测工具参数或未读过的元数据格式。

## 验证

重新选择资源并核对导入结果；在 SpriteRenderer 与相关动画/Tilemap 中验证边界、枢轴、尺寸和旧引用。
保存重载后检查子资源身份是否保持。如任务包含 Player 输出，再通过项目既有 Cook/构建流程验证载荷；仅预览成功不足以证明打包成功。
脚本生成资源时先读取当前 codec/importer，保留元数据身份，不直接复制猜测的 Unity 格式。

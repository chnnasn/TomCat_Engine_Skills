---
name: tomcat-scene-streaming
description: 实现或排查 TomCat C# 异步场景加载、激活屏障、Additive 叠加、显式卸载及持久对象。用于过场加载、地图分区和跨场景管理器。
---

# TomCat Scene Streaming

## 依据与入口

基于 TomCat v0.3.0 / `0a731be`。路径相对引擎根目录：
`Managed/TomCat.Managed/SceneManager.cs` 是签名依据，`docs/SCENE_STREAMING.zh-CN.md` 说明生命周期和失败恢复。
这是项目 C# 开发与运行验证 Skill。MCP V1 无加载/卸载场景工具；不要把 scene_save 或 entity_create 当成加载接口。
新版 Editor 的 Runtime Scenes 面板可用于 Play 中观察和手动控制；没有 UI 工具时提供操作步骤，不声称已点击。

## 实现规则

- 目标场景必须在 Build Settings 已启用列表中；整数 buildIndex 是过滤禁用项后的索引，不能照抄资源列表序号。
- `SceneManager.LoadSceneAsync(target, SceneLoadMode.Additive)` 返回 bool，true 只代表接受请求。它不是 Task 或 Unity AsyncOperation；通过 LoadState、LoadProgress、LastError 轮询，不能 await 返回值或忙等待阻塞主线程。
- Loading 控制器先把 AllowSceneActivation 设为 false，再提交加载。Reading 为读取阶段，Ready 的进度为 0.9；需要切换时设回 true，等待 Completed 和 LoadedScenes 确认。处理 Failed/Cancelled，并在退出流程恢复开关。该开关影响同步与异步请求。
- 同时只允许一个未结束异步加载。取消用 CancelPendingLoad；停止 Play 会取消后台结果。完成前原场景继续运行。
- Additive 不自动改变 ActiveScene。场景提交后按需要调用 SetActiveScene(target)，决定新建根对象默认归属。
- UnloadScene(target) 同样是帧末请求，不允许卸载最后一个场景。LoadedScenes 是已提交资产快照。
- DontDestroyOnLoad(root) 只允许根实体，保留当前子树及脚本状态。SetPersistent(root, false) 将子树归属当前活动场景；不要通过复制来模拟持久对象。

## 生命周期和验证

叠加场景共用 ECS、物理、音频、输入与脚本会话；用 Camera.Primary 明确主相机。相同资产不能重复叠加。
合入会重映射实体/脚本附件标识，不硬编码源场景 UUID。卸载后的旧引用先检查 IsAlive；跨场景子对象脱离被卸载父级时保留世界变换。
验证接受/拒绝请求、Ready 屏障、取消、失败 LastError、重复叠加拒绝、卸载范围、持久对象 OnCreate 不重复执行及 Play 停止。
后台只处理读取和摘要验证；资源/GPU/脚本激活仍在主线程，不能承诺无卡顿。卸载不强制清空共享资产缓存。
回归参考：`Tests/PhysicsRegression/src/SceneManagerRegression.h`。

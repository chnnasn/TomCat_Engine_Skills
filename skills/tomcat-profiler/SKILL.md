---
name: tomcat-profiler
description: 使用 TomCat Profiler 分析 CPU/GPU 帧耗时、Draws、资源内存及加载循环，或指导外部 C# 断点调试。用于性能诊断和证据解释。
---

# TomCat Profiler 与调试

## 依据和执行范围

基于 TomCat v0.3.0 / `0a731be`，先读引擎根目录 `docs/DEBUGGING_AND_PROFILING.md` 的相关章节。
使用 Editor 界面和导出的 CPU trace 文件。MCP V1 没有 Profiler 采样、截图、导出或断点工具；Console 日志不能代替采样数据。
若当前只有文件访问能力，可分析用户提供的 trace 或修改源码埋点，明确尚未采样的部分。

## 性能流程

打开 Window → Panels → Profiler 或 Window → Layouts → Debugging，录制后复现问题，再停止并选帧。
从 CPU Usage、GPU Usage、Rendering、Memory 选择与问题相关的指标；用 Hierarchy/Timeline 搜索 CPU scope。
更多菜单 Export CPU trace... 输出 Chrome Trace JSON。比较前后结果时保持项目、运行模式、视口、VSync 和复现步骤一致。

- CPU frame 包含 Present/VSync 等待与分析器开销；先检查等待时间。嵌套 scope 是 inclusive 耗时，不可直接相加当作整帧时间。
- GPU 是异步整帧查询，不是逐 draw 分析；pending/skipped/unavailable 不是零开销，即使曲线绘为零。CPU 减 GPU 不能推出驱动耗时。
- Draws 排除 ImGui，包含所有场景视口；submitted elements 不是去重顶点数。
- 历史最多 240 帧，每帧最多 512 个 CPU scope；检查丢弃事件。跨帧结束的后台 scope 可能被丢弃，不能当作系统级完整线程跟踪。
- 关闭面板停止采样但保留数据；Clear 清空。Dist 默认关闭 TC_PROFILE 宏，日常用 Debug/Release 分析。

## 内存与 C#

待加载完成设置 Memory baseline。重复“加载 → 游玩 → 卸载”，回到相同场景和窗口布局比较多轮资源数量、估算字节与 pending worker。
资源 payload 估算不是显存驻留；进程内存包含编辑器和 CLR。一次增长不能证明泄漏，结合缓存和字体 atlas 复用解释。

需要断点时附加支持 .NET 10 的外部 IDE 到 TomCatInut.exe。先 Play 一次初始化 .NET，再停止，附加后重新 Play 捕获 OnCreate。
使用同一次构建的 DLL/PDB，检查项目 Library/ScriptAssemblies/<build-id>/ 和 last-good.json。
项目 C# 编译为 Release；原生 Debug 不意味着 C# 无优化。PDB 把项目根映射成 `.`，缺源码时映射回项目路径。
Profiler 的 C# Debugger 页面不提供内置单步调试。停止 Play、等待脚本编译后再重启，不承诺运行中脚本热替换。
报告中区分观测、推断和未验证项；断点暂停期间的帧率不用于性能结论。

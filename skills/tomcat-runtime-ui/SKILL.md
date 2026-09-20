---
name: tomcat-runtime-ui
description: 制作或调试 TomCat Canvas UI、滑条、滚动列表、单行输入框、层级主题和本地化。用于游戏运行时界面与 C# UI 逻辑，不用于修改编辑器自身界面。
---

# TomCat Runtime UI

## 依据与执行方式

基于 TomCat v0.3.0 / `0a731be`。先按任务读取引擎根目录下的
`docs/RUNTIME_UI_PRODUCT.zh-CN.md`、`Managed/TomCat.Managed/RuntimeUI.cs` 和
`TomCat/src/TomCat/Scene/RuntimeUIComponentDescriptors.cpp`；以当前版本 C# 签名和属性描述为准。
通过编辑器 UI 或项目 C# 源码实施。当前引擎 main 未接入 Automation API；只有连接支持该协议的 Editor 并查询 component_get_schema 后，才能用其实际返回的可写字段操作组件。
ScriptAccessible 不等于 MCP 可写；不发明 UI 点击、输入模拟或本地化专用 MCP 工具。

## 构建与排查

- 在 Canvas 下配置 RectTransform 和 UIEventSystem。Inspector 的 Add Component → UI 添加组件；新版创建预设包括 Slider、Input Field、Scroll View。
- UISlider 配置 Minimum、Maximum、Value、Step 和 WholeNumbers；拖动捕获期间即使鼠标越界也应限制数值。聚焦后用方向键验证步长。
- UIScrollView 的 RectTransform 是视口，ContentSize 使用 Canvas 参考像素，Offset 从左上角计。可配合 UILayoutGroup 和普通子实体组成列表；验证父级裁剪及嵌套滚动到边缘时的传递。
- UIInputField 是单行 Unicode 输入；UIText 配置字体。验证只读、密码、粘贴过滤、字符上限、选择和删除、失焦释放输入及编辑时游戏输入屏蔽。
- UITheme 作用于自身及子树，最近的启用主题优先。ImageColor/TextColor 与已有颜色相乘，FontScale 缩放字号，非零 Font 替换字体；避免叠乘造成意外变暗。
- UILocalization 提供 Locale、FallbackLocale、Table；Table 是 YAML/JSON 的“语言 → 键 → 文本”，最多 65536 UTF-8 字节，拒绝重复键。UILocalizedText 和 UIText 放在同一实体，以 Key 查找。回退顺序为当前语言、回退语言、UIText.Text。

C# 属性访问示例（canvas、volumeEntity 是已有实体）：

```csharp
canvas.GetComponent<UILocalization>().Locale = "zh-CN";
float volume = volumeEntity.GetComponent<UISlider>().Value;
```

## 验证与限制

在 Game 视图验证 Tab/Shift+Tab 导航、射线阻挡、不同 DPI、中文/emoji 与字体回退，保存重载检查配置，停止 Play 后不要把运行时修改当作已保存。
输入法支持提交后的文字，不含预编辑与候选窗定位；字符编辑按码点，不是字素簇。滚动列表未虚拟化，无触摸惯性；本地化无复数规则/参数格式化；主题不是独立资产。
回归依据：`Tests/PhysicsRegression/src/RuntimeUIRegression.cpp` 的 `TestProductUIControls`。实机输入法行为需要单独验证。

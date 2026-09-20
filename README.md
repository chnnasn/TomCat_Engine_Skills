# TomCat Engine Skills

TomCat 编辑器的独立 **Python 客户端、MCP 服务与模块化 Agent Skills**。
外部 Agent 负责理解任务和选择工具；本仓库通过编辑器的本地 HTTP 接口执行操作，
不内置大模型，也不提供独立 Agent 的规划或记忆系统。

```text
外部 Agent + 按任务选择的 Skills
    ├── MCP stdio → tomcat-mcp ──┐
    └── Python → Client ────────┴→ 编辑器本地 HTTP → 主线程 → 场景操作
```

## 新增功能 Skill（引擎 v0.3.0）

已按引擎 main `0a731be`（2026-09-20）核对，现有自动化 Skill 之外新增 7 个可独立安装的模块：

| Skill | 使用场景 | 执行方式 |
| --- | --- | --- |
| [tomcat-prefab](skills/tomcat-prefab/SKILL.md) | 关联模板、逐属性覆盖、嵌套、变体 | Editor UI / 源码指导 |
| [tomcat-runtime-ui](skills/tomcat-runtime-ui/SKILL.md) | 滑条、滚动、输入、主题、本地化 | Editor UI / C# 开发 |
| [tomcat-scene-streaming](skills/tomcat-scene-streaming/SKILL.md) | 异步激活、叠加、卸载、持久对象 | C# 开发 / Runtime Scenes |
| [tomcat-profiler](skills/tomcat-profiler/SKILL.md) | CPU/GPU、资源内存、外部断点 | Editor UI / trace 分析 |
| [tomcat-assets](skills/tomcat-assets/SKILL.md) | 资源 Inspector、导入、Atlas | Editor UI / 源码指导 |
| [tomcat-animation](skills/tomcat-animation/SKILL.md) | Clip、Controller、参数与过渡 | Editor UI / 源码指导 |
| [tomcat-tilemap](skills/tomcat-tilemap/SKILL.md) | Grid、Palette、地图绘制 | Editor UI / 源码指导 |

**该引擎 main 基线不含原生 Automation API。** 新 Skill 可指导 Agent 编写项目代码、分析源码，或通过可用 UI 工具操作编辑器；它们没有新增 MCP 执行接口。MCP 仍为 18 个工具，需要另行提供已集成 Automation API 的 Editor。仅安装本包不会给 main 增加 HTTP 服务，`list` 输出也不证明 Editor 支持这些工具。

每个 Skill 标明引擎源码相对路径、操作步骤、验证方式和功能限制。使用其他版本时重新核对对应实现；引擎源码根目录与游戏项目根目录应分别识别。没有源码或 UI 操作能力时，Agent 应说明缺少的执行依据，不声称已操作编辑器。

## 仓库边界

| 本仓库 | TomCat_Engine 引擎仓库 |
| --- | --- |
| 可安装的 Python 包、MCP 工具定义 | HTTP 服务、参数与目标校验 |
| Skill 操作指南与启动脚本 | 场景和组件编辑、撤销、运行控制 |
| 客户端测试、跨仓库集成测试入口 | C++ 编译、引擎实现、示例游戏 |

日常使用只需要安装本包并连接支持自动化协议的 Editor，不需要引擎源码。
从源码编译 Editor、运行集成回归，或按新增 Skill 核对实现时，需要指定引擎仓库。

## 安装

Python 3.10+。当前编辑器运行于 Windows x64；客户端单元测试可独立运行。

```powershell
git clone https://github.com/chnnasn/TomCat_Engine_Skills.git
cd TomCat_Engine_Skills
python -m venv .venv
# 安装客户端、MCP 服务和随包分发的 Skill 文件
.venv/Scripts/python.exe -m pip install ".[mcp]"
```

仅使用 Python/CLI 客户端时，安装 `.` 即可，运行时无第三方依赖。
开发时使用 `pip install -e ".[mcp]"`。本包尚未声明已发布到 PyPI，
安装源以包含这些文件的本地工作区或 Git 版本为准。

## 通用连接配置

Skill 不绑定某台电脑、安装目录或项目。安装后，MCP 可以只配置命令：

```json
{
  "mcpServers": {
    "tomcat-editor": {
      "command": "tomcat-mcp"
    }
  }
}
```

前提是 **启动 Agent 的进程 PATH 能找到 tomcat-mcp**。本地虚拟环境安装可在激活 `.venv` 后从同一终端启动 Agent；桌面启动的 Agent 不一定继承这个环境。也可使用已加入 PATH 的 Python 工具环境安装本包。若宿主不支持 PATH 查找，则填写实际 `tomcat-mcp` 可执行文件路径，这属于宿主安装配置，Skill 不依赖它。Windows 虚拟环境中的命令位于 `.venv/Scripts/tomcat-mcp.exe`。

在当前用户主目录创建 `.tomcat/automation.json`（Windows 通常为 `%USERPROFILE%/.tomcat/automation.json`），集中保存连接参数：

```json
{
  "project": "/absolute/path/to/YourGame.tcproj",
  "port": 8091,
  "token": "REPLACE_WITH_THE_EDITOR_TOKEN"
}
```

这是本机配置示例，不是仓库固定路径：project 改为实际项目，token 使用与 Editor 一致的随机令牌（至少 16 字符，可用 `[guid]::NewGuid().ToString('N')` 生成）。文件含令牌，应只保存在本机，不提交到项目仓库。port 可省略，默认 8091。

字段优先级为 **显式 Client 参数 / CLI --project → 环境变量 → 连接文件 → 默认端口**。原有 `TOMCAT_PROJECT`、`TOMCAT_AUTOMATION_PORT`、`TOMCAT_AUTOMATION_TOKEN` 配置继续有效。文件里的相对 project 路径相对配置文件目录解析；显式参数/环境变量的相对路径相对进程工作目录解析。

多项目可分别保存连接文件，用 `tomcat-mcp --config <文件路径>`、`tomcat-skills --config <文件路径> editor_get_status` 或 `TOMCAT_AUTOMATION_CONFIG` 选择。显式指定的文件缺失会报错，不会退回其他项目。配置在进程启动时读取，切换项目/令牌后重启 MCP；不会扫描端口、猜测令牌或自动切到别的 Editor。

## 启动 Editor

需要带有 Automation API 的 TomCat Editor，协议版本为 **1**。本 Python 包读取连接文件；引擎仍通过环境变量启用 HTTP，尚不会自动读取这个文件。

以下 PowerShell 示例读取同一配置，避免两处手工填写。project 使用绝对路径，Editor 路径通过交互输入：

```powershell
$connection = Get-Content (Join-Path $HOME '.tomcat/automation.json') -Raw | ConvertFrom-Json
$env:TOMCAT_AUTOMATION_PORT = if ($null -eq $connection.port) { '8091' } else { [string]$connection.port }
$env:TOMCAT_AUTOMATION_TOKEN = $connection.token
$env:TOMCAT_PROJECT = $connection.project
$editorExecutable = Read-Host 'Editor executable path'
& $editorExecutable $env:TOMCAT_PROJECT
```

Editor 未设置端口时默认关闭自动化服务。端口占用或令牌不足 16 字符时启动服务失败。多个 Editor 使用不同端口；配置文件不会自动启动 Editor，也不能给缺少 Automation API 的引擎添加服务。

MCP 不需要指定仓库工作目录、PYTHONPATH 或引擎源码路径。连接后先调用 `editor_get_status`、`component_get_schema` 和 `scene_get_tree` 核对项目与能力；项目匹配和编辑器会话检查仍保留。

## 使用客户端和 Skill

客户端与 MCP 共用上述配置文件和环境变量。CLI 示例（命令已在 PATH 中）：

```powershell
tomcat-skills list
tomcat-skills editor_get_status
tomcat-skills scene_get_tree '{"limit":20}'
```

Python 多步操作使用同一个 Client，保留失败重试所需的请求记录：

```python
from tomcat_skills.client import Client

editor = Client()
status = editor.call("editor_get_status")
schema = editor.call("component_get_schema")
entities = editor.call("scene_get_tree", {"limit": 20})
```

从 `skills/` 选择需要的模块，将各个 `tomcat-*` 完整目录复制到 Agent 支持的技能目录，可一次安装全部 8 个；不要只复制 SKILL.md。
[tomcat-editor](skills/tomcat-editor/SKILL.md) 优先使用 MCP 工具；没有 MCP 时，其 `scripts/tomcat.py`
可通过**已安装本包的 Python**执行。无需旧版的 `TOMCAT_AUTOMATION_HOME`。

wheel 安装也会把 Skill 文件放入 Python 环境下的
`share/tomcat-engine-skills/skills/`，可从那里复制各个完整模块目录。
安装 Python 包本身不会修改 Agent 的全局配置。

## 能力与兼容范围

V1 提供 **18 个工具**：状态、实体树、组件 Schema、实体属性、Console 日志，
实体创建/删除/换父级，组件添加/移除/属性修改，Play/Pause/Step/Stop，
已有路径的场景保存，以及 Undo/Redo。

64 位 ID 用十进制字符串传输。编辑操作由引擎校验、在场景副本中执行，再发布到主线程
并接入撤销；停止运行会恢复编辑状态。协议通过 `protocol_version=1` 检查兼容性，
组件名称、ID 与可写字段以连接中的 Editor 返回的 Schema 为准。

MCP 目前不提供截图、资源导入、脚本编辑、构建任务或批量事务；本仓库不内置独立 Agent。
新增 Skill 中的源码开发和 UI 操作依赖外部 Agent 已有能力。
未保存过的场景需要先在 Editor 中执行一次 Save As。
详细请求约定、错误与重试语义见 [协议说明](docs/protocol.md)。

## 测试

独立单元测试无需引擎源码或 Editor：

```powershell
.venv/Scripts/python.exe -m unittest discover -s tests -p 'test_*.py' -v
```

真实编辑器与 MCP 集成测试需指定已包含原生 Automation API 的引擎检出，目录无需相邻。
上述 v0.3.0 main 基线不能直接运行此回归；先确认 Editor 已集成协议，再执行：

```powershell
& scripts/Run-AutomationRegression.ps1 -EngineRoot E:/Github/TomCat_Engine
# 已有最新 Release Editor 时可添加 -SkipBuild。
```

脚本复制 PhysicsPlayground 到独立临时目录，启动自己的隐藏 Editor，
验证编辑、撤销、请求去重、物理步进及 MCP stdio，最后只关闭自己启动的进程。
日志和临时项目保留用于诊断，原示例不会被修改。

## 目录

```text
src/tomcat_skills/       Python 包、CLI 与 MCP 服务
skills/tomcat-*/         8 个可独立复制安装的 Agent Skills
tests/                  客户端与真实 Editor 测试
scripts/                跨仓库回归入口
docs/                   协议与行为约定
pyproject.toml          包元数据、依赖和命令入口
```

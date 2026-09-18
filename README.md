# TomCat Engine Skills

TomCat 编辑器的独立 **Python 客户端、MCP 服务与 Agent Skill**。
外部 Agent 负责理解任务和选择工具；本仓库通过编辑器的本地 HTTP 接口执行操作，
不内置大模型，也不提供独立 Agent 的规划或记忆系统。

```text
外部 Agent + tomcat-editor Skill
    ├── MCP stdio → tomcat-mcp ──┐
    └── Python → Client ────────┴→ 编辑器本地 HTTP → 主线程 → 场景操作
```

## 仓库边界

| 本仓库 | TomCat_Engine 引擎仓库 |
| --- | --- |
| 可安装的 Python 包、MCP 工具定义 | HTTP 服务、参数与目标校验 |
| Skill 操作指南与启动脚本 | 场景和组件编辑、撤销、运行控制 |
| 客户端测试、跨仓库集成测试入口 | C++ 编译、引擎实现、示例游戏 |

日常使用只需要安装本包并连接支持自动化协议的 Editor，不需要引擎源码。
只有从源码编译 Editor、运行本仓库的集成回归时才需要指定引擎仓库。

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

## 启动 Editor

需要带有 Automation API 的 TomCat Editor，协议版本为 **1**。
旧版 Editor 仅安装本 Python 包不会自动获得这些能力。

在启动 Editor 的 PowerShell 中设置：

```powershell
$env:TOMCAT_AUTOMATION_PORT = '8091'
$env:TOMCAT_AUTOMATION_TOKEN = [guid]::NewGuid().ToString('N')
$env:TOMCAT_PROJECT = 'C:/MyGame/Project.tcproj'
& 'C:/TomCat/TomCat.exe' $env:TOMCAT_PROJECT
```

Editor 未设置端口时默认关闭自动化服务。端口占用或令牌不足 16 字符时启动服务失败，
不会自动连接到别的实例。每个 Editor 使用不同端口；客户端与 Editor 使用相同令牌。
令牌保存在本地环境或客户端设置中，不要提交到 Git。

## 接入 MCP

以下为通用 stdio 配置示例；根据客户端调整外层配置格式，替换安装路径、项目路径和令牌。
MCP 服务进程不需要指定工作目录，也不需要 `PYTHONPATH` 或引擎源码路径。

```json
{
  "mcpServers": {
    "tomcat-editor": {
      "command": "E:/Github/TomCat_Engine_Skills/.venv/Scripts/python.exe",
      "args": ["-m", "tomcat_skills.server"],
      "env": {
        "TOMCAT_PROJECT": "C:/MyGame/Project.tcproj",
        "TOMCAT_AUTOMATION_PORT": "8091",
        "TOMCAT_AUTOMATION_TOKEN": "REPLACE_WITH_THE_EDITOR_TOKEN"
      }
    }
  }
}
```

也可以直接把 `.venv/Scripts/tomcat-mcp.exe` 配置成 command，不传 args。
先调用 `editor_get_status`、`component_get_schema` 和 `scene_get_tree` 确认连接与能力。

## 使用客户端和 Skill

客户端使用与 MCP 相同的三个环境变量。CLI 示例：

```powershell
.venv/Scripts/tomcat-skills.exe list
.venv/Scripts/tomcat-skills.exe editor_get_status
.venv/Scripts/python.exe -m tomcat_skills scene_get_tree '{"limit":20}'
```

Python 多步操作使用同一个 Client，保留失败重试所需的请求记录：

```python
from tomcat_skills.client import Client

editor = Client()
status = editor.call("editor_get_status")
schema = editor.call("component_get_schema")
entities = editor.call("scene_get_tree", {"limit": 20})
```

把 [skills/tomcat-editor](skills/tomcat-editor/SKILL.md) 整个目录复制到 Agent
支持的技能目录。Skill 优先使用 MCP 工具；没有 MCP 时，其 `scripts/tomcat.py`
可通过**已安装本包的 Python**执行。无需旧版的 `TOMCAT_AUTOMATION_HOME`。

wheel 安装也会把 Skill 文件放入 Python 环境下的
`share/tomcat-engine-skills/skills/tomcat-editor`，可从那里复制完整目录。
安装 Python 包本身不会修改 Agent 的全局配置。

## 能力与兼容范围

V1 提供 **18 个工具**：状态、实体树、组件 Schema、实体属性、Console 日志，
实体创建/删除/换父级，组件添加/移除/属性修改，Play/Pause/Step/Stop，
已有路径的场景保存，以及 Undo/Redo。

64 位 ID 用十进制字符串传输。编辑操作由引擎校验、在场景副本中执行，再发布到主线程
并接入撤销；停止运行会恢复编辑状态。协议通过 `protocol_version=1` 检查兼容性，
组件名称、ID 与可写字段以连接中的 Editor 返回的 Schema 为准。

目前不提供截图、资源导入、脚本编辑、构建任务、批量事务和独立 Agent。
未保存过的场景需要先在 Editor 中执行一次 Save As。
详细请求约定、错误与重试语义见 [协议说明](docs/protocol.md)。

## 测试

独立单元测试无需引擎源码或 Editor：

```powershell
.venv/Scripts/python.exe -m unittest discover -s tests -p 'test_*.py' -v
```

真实编辑器与 MCP 集成测试需明确指定引擎仓库，目录无需相邻：

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
skills/tomcat-editor/    可复制安装的 Agent Skill
tests/                  客户端与真实 Editor 测试
scripts/                跨仓库回归入口
docs/                   协议与行为约定
pyproject.toml          包元数据、依赖和命令入口
```

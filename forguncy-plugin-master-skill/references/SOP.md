# 活字格插件开发标准作业程序 (SOP) —— 简洁版

本 SOP 旨在提供高效、标准化的开发流程，确保插件的“简洁与安全”。

## 阶段一：环境与初始化 (Setup)
1. **环境检查**：安装 .NET SDK (6.0+) 及活字格设计器。
2. **项目创建**：运行 `scripts/InitProject.ps1`。
3. **产出**：获取包含 `.csproj` 和基础代码的项目结构。

## 阶段二：需求分析与计划 (Planning)
1. **创建计划**：在 `plans/` 下创建 `序号_需求描述.md`。
2. **内容要求**：
   - **分析**：明确目标。
   - **引用**：必须链接至 `references/` 中的规范文档。
   - **设计**：规划属性与核心逻辑。
3. **确认**：用户确认计划后方可开始编码。

## 阶段三：定义与属性设计 (Design)
1. **类型决策**：参考 `Decision_Tree.md`。
2. **属性定义**：
   - 遵循 `Unified_Properties.md`。
   - 必须使用 `[DisplayName]`。
   - 布尔值默认 True 时必须加 `[DefaultValue(true)]`。
3. **极简 API**：严禁暴露内部参数，优先内部推导。

## 阶段四：核心实现 (Implementation)
1. **服务端 (C#)**：
   - 数据库：强制使用 `this.Context.DataAccess` + 参数化查询。
   - 日志：使用 `this.Context.Logger`，禁止 `Console.WriteLine`。
2. **前端 (JS)**：
   - **同步约束**：生命周期方法严禁 `async`。
   - **逻辑复用**：提取数据转换纯函数，确保 `onRender` 与 `updateData` 一致。
   - **埋点**：带有 `[PluginName]` 前缀的日志记录。

## 阶段五：构建、测试与维护 (Maintenance)
1. **构建**：`dotnet build`。若配置了 `ForguncyPluginPackageTool`，构建成功即自动打包。
2. **验证**：在设计器安装并测试功能，检查 F12 控制台日志。
3. **重构**：删除类文件后必须清理 `PluginConfig.json` 中的无效引用。
4. **修复**：若引用丢失，运行 `scripts/update_references.ps1`。

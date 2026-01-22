# 服务端命令插件基本结构

本文描述了一个标准的服务端命令插件所必须包含的代码结构和基础要素。任何服务端命令插件的开发都应遵循此基本范式。

## 1. 核心要素

一个最小化的服务端命令插件类必须包含：
1.  **类定义**：继承 `Command` 基类并实现 `ICommandExecutableInServerSideAsync` 接口。
2.  **属性定义**：使用特性（Attributes）标记的公共属性，用于接收用户配置。
3.  **执行逻辑**：实现 `ExecuteAsync` 方法，这是命令运行时的入口点。
4.  **元数据**：重写 `ToString()` 和 `GetCommandScope()`，定义设计器显示名称和作用域。

## 2. 标准代码模板

```csharp
using System.ComponentModel;
using System.Threading.Tasks;
using GrapeCity.Forguncy.Commands;
using GrapeCity.Forguncy.Plugin;

namespace MyPlugin
{
    // 指定插件图标路径
    [Icon("pack://application:,,,/MyPlugin;component/Resources/Icon.png")]
    public class AddNumbersCommand : Command, ICommandExecutableInServerSideAsync
    {
        // 输入参数1：支持公式（如 =A1 或直接输入数字）
        [FormulaProperty]
        [DisplayName("加数1")]
        public object AddNumber1 { get; set; }

        // 输入参数2
        [FormulaProperty]
        [DisplayName("加数2")]
        public object AddNumber2 { get; set; }

        // 输出参数：用于接收计算结果的变量名
        // ResultToProperty 特性告诉设计器这是一个变量选择器
        [ResultToProperty]
        [DisplayName("相加结果")]
        public string ResultTo { get; set; } = "结果"; // 默认变量名为“结果”

        public async Task<ExecuteResult> ExecuteAsync(IServerCommandExecuteContext dataContext)
        {
            // 1. 计算公式的值（因为 AddNumber 可能是公式 "=1+2" 也可能是变量 "=Var1"）
            var val1 = await dataContext.EvaluateFormulaAsync(AddNumber1);
            var val2 = await dataContext.EvaluateFormulaAsync(AddNumber2);

            // 2. 类型转换
            double.TryParse(val1?.ToString(), out var num1);
            double.TryParse(val2?.ToString(), out var num2);

            // 3. 执行核心逻辑
            var sum = num1 + num2;

            // 4. 将结果回写到上下文变量中
            // dataContext.Parameters 字典用于读写流程中的变量
            dataContext.Parameters[ResultTo] = sum;

            // 5. 返回执行成功
            return new ExecuteResult();
        }

        // 定义在设计器命令列表中显示的名称
        public override string ToString()
        {
            return "两数相加";
        }

        // 定义命令的作用域（仅服务端可用）
        public override CommandScope GetCommandScope()
        {
            return CommandScope.ExecutableInServer;
        }
    }
}
```

## 3. 关键点解析

### ICommandExecutableInServerSideAsync 接口
- **旧版接口**：`ICommandExecutableInServerSide` (同步方法 Execute)
- **新版接口**：`ICommandExecutableInServerSideAsync` (异步方法 ExecuteAsync)
- **推荐做法**：始终使用 `Async` 版本。在服务端高并发场景下，异步执行能显著提升性能，避免阻塞线程池。

### 属性特性
- `[FormulaProperty]`：允许用户输入常量或公式（如 `=A1`）。这是处理动态参数的标准方式。
- `[ResultToProperty]`：标记该属性用于存储结果。设计器会提供一个变量选择器，方便用户选择将结果存入哪个变量。

### 数据回写
- `dataContext.Parameters[VariableName] = value;` 是将数据回传给活字格引擎的标准方式。后续的命令可以通过该变量名获取到这个值。

# 添加属性 - 布尔属性 (Boolean Property)

在服务端命令插件开发中，布尔属性用于接收用户输入的 `True/False` 值，通常在设计器中显示为复选框（Checkbox）。

## 1. 默认布尔属性
默认情况下，如果属性类型是 `bool`，活字格会自动识别为布尔属性。

### 代码示例
```csharp
public class MyPluginServerCommand : Command, ICommandExecutableInServerSideAsync
{
    [DisplayName("启用日志")]
    public bool EnableLogging { get; set; }

    public async Task<ExecuteResult> ExecuteAsync(IServerCommandExecuteContext dataContext)
    {
        return new ExecuteResult();
    }
}
```

---

## 2. 高级配置 (BoolPropertyAttribute)
使用 `[BoolProperty]` 特性可以控制复选框的缩进级别，使属性面板具有更好的视觉层次。

### 2.1 控制缩进 (IndentLevel)
通过 `IndentLevel` 属性设置缩进等级，默认值为 0。

```csharp
public class MyPluginServerCommand : Command, ICommandExecutableInServerSideAsync
{
    [DisplayName("开启高级模式")]
    [BoolProperty(IndentLevel = 0)]
    public bool AdvancedMode { get; set; }

    [DisplayName("忽略错误")]
    [BoolProperty(IndentLevel = 1)] // 缩进一级，看起来像是上一项的子选项
    public bool IgnoreErrors { get; set; }

    [DisplayName("自动重试")]
    [BoolProperty(IndentLevel = 1)]
    public bool AutoRetry { get; set; }
}
```

## 3. 常见陷阱：默认值设置
**重要提示**：如果希望布尔属性的默认值为 `true`，**必须**同时做两件事：
1. 在 C# 属性初始化器中设为 `true`。
2. 添加 `[DefaultValue(true)]` 特性。

如果只做了第 1 步而没有添加 `[DefaultValue(true)]`，设计器可能无法正确保存该属性的默认状态。

**正确示例：**
```csharp
public class MyPluginServerCommand : Command, ICommandExecutableInServerSideAsync
{
    [DisplayName("默认开启")]
    [DefaultValue(true)] // 必须添加！
    public bool IsActive { get; set; } = true; // 必须初始化！

    public async Task<ExecuteResult> ExecuteAsync(IServerCommandExecuteContext dataContext)
    {
        return new ExecuteResult();
    }
}
```

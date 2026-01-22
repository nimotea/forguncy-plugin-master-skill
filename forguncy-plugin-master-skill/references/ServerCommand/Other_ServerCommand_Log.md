# 服务端命令日志 (Server Command Log)

在服务端命令执行过程中，记录日志对于调试、监控和错误排查非常重要。活字格通过 `IServerCommandExecuteContext.Log` 提供了标准的日志记录功能。

## 日志对象

在 `ExecuteAsync` 方法中，可以通过 `dataContext.Log` 获取日志对象。该对象类型为 `StringBuilder`（或类似接口），主要用于追加文本日志。

## 代码示例

```csharp
public class MyPluginServerCommand : Command, ICommandExecutableInServerSideAsync
{
    public async Task<ExecuteResult> ExecuteAsync(IServerCommandExecuteContext dataContext)
    {
        // 1. 记录简单文本
        dataContext.Log.AppendLine("插件开始执行...");

        try 
        {
            // 2. 记录变量值或中间状态
            int userId = 123;
            dataContext.Log.AppendLine($"当前处理的用户 ID: {userId}");

            // 执行业务逻辑...
            await Task.Delay(100);

            dataContext.Log.AppendLine("业务逻辑执行完毕。");
        }
        catch (Exception ex)
        {
            // 3. 记录异常信息
            // 注意：如果抛出异常，活字格会自动记录异常堆栈，但手动记录可以提供更多上下文
            dataContext.Log.AppendLine($"执行过程中发生错误: {ex.Message}");
            throw; // 重新抛出异常让框架处理
        }

        return new ExecuteResult();
    }

    public override CommandScope GetCommandScope()
    {
        return CommandScope.ExecutableInServer;
    }
}
```

## 日志查看

记录的日志可以在活字格管理控制台的“日志”部分查看。

- **调试阶段**：在设计器中使用“模拟运行”时，日志通常会输出到“输出”窗口或模拟运行的日志面板中。
- **运行阶段**：发布到服务器后，日志会被记录到系统日志文件中，管理员可以通过管理控制台查看。

## 最佳实践

1.  **适度记录**：不要记录过于频繁或冗余的信息，以免日志文件过大影响性能。
2.  **关键节点**：在流程的开始、结束、重要分支和异常捕获处记录日志。
3.  **包含上下文**：记录日志时尽量包含当前的上下文信息（如关键参数、ID 等），以便于定位问题。
4.  **安全隐私**：**严禁**在日志中记录敏感信息（如密码、密钥、个人隐私数据等）。

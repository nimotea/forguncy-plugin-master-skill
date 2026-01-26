# SDK 最佳实践 (Best Practices)

## 1. IGenerateContext 的使用
`IGenerateContext` 是你访问服务器端环境的入口。它提供了对数据库、用户信息和公式计算的访问权限。

- **务必**：如果辅助方法 (helper methods) 需要访问环境，请将 `IGenerateContext` 向下传递给它们。
- **严禁**：将 `IGenerateContext` 缓存到静态变量中，因为它是请求作用域 (request-scoped) 的。

## 2. 数据访问 (Data Access)
使用内置的 `context.DataAccess` 与数据库进行交互。

- **正确做法**：
  ```csharp
  context.DataAccess.ExecuteNonQuery("UPDATE Table SET Column = @Val", new { Val = 123 });
  ```
- **禁止做法**：
  ```csharp
  using (var conn = new SqlConnection("...")) // 请勿这样做
  {
      // ...
  }
  ```
  **原因**：`context.DataAccess` 在活字格环境中自动处理事务范围和连接池。自行创建连接会破坏事务链，并可能导致数据不一致。

## 3. 参数安全 (Parameter Safety)
当接受用户输入时（例如，通过公式计算得到的属性值）：

- **净化 (Sanitize)**：始终假设输入是不可信的。
- **参数化查询**：切勿将字符串拼接进 SQL 查询中。请使用参数。
  ```csharp
  // 错误示范
  context.DataAccess.ExecuteNonQuery($"SELECT * FROM Users WHERE Name = '{name}'");
  
  // 正确示范
  context.DataAccess.ExecuteNonQuery("SELECT * FROM Users WHERE Name = @Name", new { Name = name });
  ```
## 4. 命令显示名称 (ToString 实现)
活字格设计器在命令列表中显示命令的方式取决于 `ToString()` 方法的返回值。

- **痛点**：默认的 `ToString()` 实现可能只显示类名，或者被重写为仅显示参数（如 "Value1"），导致用户在查看长长的命令列表时，不知道每个命令到底是什么。
- **最佳实践**：始终在 `ToString()` 的返回值中包含命令的名称（或 `DisplayName`）。
- **推荐格式**：`"命令名称: 关键参数描述"`
- **进阶做法（推荐）**：在基类中提取辅助方法，避免在每个子类中重复编写逻辑。
  ```csharp
  protected string FormatDescription(object content, string descriptionPattern = "{0}")
  {
      var displayName = this.GetType().GetCustomAttribute<DisplayNameAttribute>()?.DisplayName ?? this.GetType().Name;
      if (content == null || string.IsNullOrWhiteSpace(content.ToString())) return displayName;
      return $"{displayName}: {string.Format(descriptionPattern, content)}";
  }

  // 子类实现极其简洁
  public override string ToString() => FormatDescription(Url, "从[={0}]下载");
  ```
- **示例**：
  ```csharp
  public override string ToString()
  {
      // 假设该命令的 DisplayName 是 "发送短信"
      // 关键参数是手机号和模板
      return $"发送短信: {PhoneNumber} (模板: {TemplateId})";
  }
  ```
- **注意**：如果 `ToString()` 返回空字符串或纯空格，活字格可能会显示默认的类名，但这通常不是最佳体验。确保返回值对非技术用户友好。

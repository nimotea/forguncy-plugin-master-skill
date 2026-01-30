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

## 5. 版本与元数据管理 (Version Control)
为了避免版本混乱，推荐以下流程：
1. **单一数据源**：将 `PluginConfig.json` 视为版本的 Source of Truth。
2. **构建前检查**：在发布或构建前，先更新 `PluginConfig.json` 中的版本号。
3. **自动化同步**：使用脚本在构建时自动将 JSON 中的版本号同步到 `.csproj` 的 `<Version>` 节点。

**错误示范**：
- 手动分别修改 JSON 和 CSPROJ，导致不一致。
- 发布了新功能但忘记修改 Version，导致用户无法更新。

## 6. 前端运行时日志埋点规范

在插件渲染（`onRender`）或执行（`execute`）过程中，应包含关键节点的日志输出，以便于在生产环境中快速定位问题。

- **统一前缀**：所有日志必须带有 `[PluginName]` 前缀。
- **关键节点**：
    - **入口点**：记录接收到的原始参数。
    - **数据处理后**：记录转换后的渲染数据。
    - **渲染完成**：记录最终挂载或库初始化的状态。
- **性能控制**：生产环境建议仅保留错误和关键警告日志。

```javascript
// 示例：在单元格类型中埋点
onRender(container, renderInfo) {
    console.log("[MyPlugin]: Start rendering...", renderInfo);
    
    const data = this.processData(renderInfo.Value);
    if (!data) {
        console.warn("[MyPlugin]: Data is empty, skipping chart update.");
        return;
    }
    console.log("[MyPlugin]: Processed data:", data);

    try {
        this.chart.update(data);
    } catch (e) {
        console.error("[MyPlugin]: Chart update failed:", e);
    }
}
```

## 7. C# 与 JS 枚举同步 (Enum Synchronization)

当插件在 C# 端使用 `enum` 定义配置项，而在 JS 端需要根据这些值进行逻辑分发时，**严禁使用魔法数字 (Magic Numbers)**。

- **痛点**：C# 枚举的默认序列化结果是整数（0, 1, 2...）。如果 C# 端枚举顺序调整或插入新项，JS 端硬编码的数字将全部失效且难以排查。
- **最佳实践**：在 JS 代码顶部显式定义一个与 C# 枚举结构一致的常量对象，并在逻辑中使用该对象。

### 推荐模式

**C# 端定义：**
```csharp
public enum ChartType
{
    Bar = 0,
    Line = 1,
    Pie = 2
}
```

**JS 端实现：**
```javascript
// 1. 定义映射对象（作为常量）
const ChartType = {
    Bar: 0,
    Line: 1,
    Pie: 2
};

// 2. 在逻辑中使用常量，而非数字
class MyPlugin extends Forguncy.Plugin.CellTypeBase {
    createContent() {
        // this.CellElement.CellType.ChartType 是从 C# 传来的整数
        const type = this.CellElement.CellType.ChartType;

        switch (type) {
            case ChartType.Bar:  // ✅ 可读性强，易于维护
                return this.renderBar();
            case ChartType.Line:
                return this.renderLine();
            default:
                console.warn(`Unknown chart type: ${type}`);
        }
    }
}
```
        console.log("[MyPlugin]: Render complete.");
    } catch (e) {
        console.error("[MyPlugin]: Render failed!", e);
    }
}
```

### 4. DOM 尺寸获取的最佳实践 (waitForSize)

在 `createContent` 或 `onPageLoaded` 阶段，如果你使用的第三方库（如 ECharts, G2, Spreadsheet）需要容器的宽高进行初始化，请注意：**活字格的 DOM 挂载是异步的**。

- **风险**：直接调用 `container.width()` 可能返回 `0`，导致初始化失败或渲染异常。
- **解决方案**：使用“尺寸检测轮询模式”，直到容器真正具有尺寸后再执行逻辑。

```javascript
// 推荐的辅助函数模式
waitForSize(container, callback) {
    const checkSize = () => {
        const width = container.width();
        const height = container.height();
        if (width > 0 && height > 0) {
            callback(width, height);
        } else {
            // 每 50ms 检查一次，最多等待一段时间
            requestAnimationFrame(checkSize);
        }
    };
    checkSize();
}

// 使用示例
onPageLoaded() {
    this.waitForSize(this.container, (w, h) => {
        console.log(`[MyPlugin]: Container ready (${w}x${h}), initializing chart...`);
        this.initChart(w, h);
    });
}
```

### 5. 生命周期异步限制 (JS)

在编写 JavaScript 插件（如单元格类型、自定义命令）时，必须严格遵守活字格的生命周期同步性要求。

- **严禁使用 async**：`createContent`、`onRender`、`destroy` 等生命周期方法**绝对禁止**声明为 `async`。
- **后果**：活字格框架不等待这些方法返回的 `Promise`。如果你将 `createContent` 设为异步，它会立即返回一个 Promise 而不是 DOM 元素，导致单元格显示为空白，且控制台通常不会报错（静默失败）。
- **正确处理异步逻辑**：
    - 如果需要获取公式值（`evaluateFormulaAsync`），应在同步方法中发起请求，并在 `.then()` 回调中更新 DOM。
    - 结合“尺寸检测轮询模式”或“状态标记”来处理数据到达后的重绘。

```javascript
// 错误示范：会导致显示空白
async createContent() {
    const val = await this.evaluateFormulaAsync(...); 
    return $("<div>" + val + "</div>"); // 框架无法处理这个返回
}

// 正确示范：同步返回占位符，异步更新
createContent() {
    const container = $("<div>Loading...</div>");
    this.evaluateFormulaAsync(...).then(val => {
        container.text(val); // 数据到达后更新内容
    });
    return container; // 必须同步返回 DOM
}
```

## 6. 属性默认值规范 (C#)

在定义插件属性时，如果初始值不是该类型的默认值（如 `bool` 默认为 `false`，引用类型默认为 `null`），必须显式处理。

- **重要风险**：如果一个布尔属性的默认值设为 `true`，但没有添加 `[DefaultValue(true)]` 特性，活字格设计器在用户将其设置为 `false` 时可能无法正确识别出“非默认状态”，从而导致配置无法保存或丢失。
- **强制规范**：
    - 任何布尔属性如果初始值设为 `true`，**必须**同时添加 `[DefaultValue(true)]` 特性。
    - 同样适用于其他非标准默认值的类型（如 `int` 默认为 `100`）。

**正确示例**：
```csharp
[DisplayName("启用缓存")]
[DefaultValue(true)] // 必须显式标注
public bool EnableCache { get; set; } = true;
```

**错误示例**：
```csharp
[DisplayName("启用缓存")]
public bool EnableCache { get; set; } = true; // 缺少 DefaultValueAttribute，会导致 False 状态无法保存
```

## 7. 其他建议
- **异常处理**：不要吞掉异常。让错误适当地向上冒泡，以便活字格可以记录它们。
- **日志记录**：利用活字格的日志记录机制（如果 SDK 暴露了的话）来记录调试信息。

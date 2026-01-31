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

## 8. C# 与 JS 配置同步 (Configuration Sync)

在开发复杂的可视化或 UI 插件时，经常需要将大量 C# 属性（如颜色、字体、边框等）映射到 JS 第三方库的配置对象中。

- **痛点**：C# 属性名（PascalCase）与 JS 库配置项（camelCase 或 snake_case）通常不一致，导致 JS 代码中充斥着大量的 `if/else` 或三元运算符赋值逻辑，繁琐且易错。
- **最佳实践**：编写一个通用的 `applySettings` 辅助函数，通过映射表批量处理配置同步。

### 推荐模式

**JS 端辅助函数：**

```javascript
/**
 * 批量应用配置
 * @param {Object} target - 目标对象 (如 options)
 * @param {Object} source - 源数据 (this.CellElement.CellType)
 * @param {Object} mapping - 映射表 { "JS配置名": "CSharp属性名" }
 */
applySettings(target, source, mapping) {
    for (const [jsKey, csKey] of Object.entries(mapping)) {
        const value = source[csKey];
        if (value !== undefined && value !== null) {
            target[jsKey] = value;
        }
    }
}
```

**使用示例：**

```javascript
createContent() {
    const cellType = this.CellElement.CellType;
    
    // 第三方库的默认配置
    const chartOptions = {
        title: "Default",
        showLegend: true,
        themeColor: "#000"
    };

    // 定义映射关系：左边是 JS 库需要的 key，右边是 C# 定义的属性名
    const propertyMapping = {
        "title": "TitleText",
        "showLegend": "ShowLegend",
        "themeColor": "ThemeColor"
    };
    
    // 一键同步，自动忽略 C# 端未定义的属性
    this.applySettings(chartOptions, cellType, propertyMapping);
    
    // ... 初始化组件
}
```

## 9. 默认开启的布尔属性 (Boolean Default True Pattern)

在活字格插件开发中，如果你需要一个**默认开启**（Default True）且支持用户取消勾选的布尔属性，直接使用标准的 `[DefaultValue(true)]` 可能会导致 JS 端逻辑处理困难。

-   **场景**：你需要一个显示边框的属性，默认勾选（True）。
-   **标准做法的问题**：
    -   如果设 `[DefaultValue(true)]` 且初始值为 `true`，设计器保存时会省略该字段（因为值等于默认值）。
    -   JS 端读取到的值为 `undefined`。
    -   JS 代码必须显式处理 `undefined` 为 `true`（例如 `const show = (val === undefined) ? true : val`）。
    -   如果 JS 开发者习惯使用简单的 Falsy 判断（`if (options.showBorder)`），则会因为 `undefined` 被视为 false 而导致默认关闭，逻辑出错。

-   **推荐模式（Hack 方案）**：
    利用 Forguncy 的序列化机制反向操作，确保开启状态始终被序列化，而关闭状态作为默认值（空）。

    **C# 端定义：**
    ```csharp
    // 1. 标记 DefaultValue 为 false (欺骗序列化器)
    [DefaultValue(false)]
    [DisplayName("显示边框")]
    // 2. 实际属性初始值设为 true (业务需求默认开启)
    public bool ShowBorder { get; set; } = true;
    ```

    **机制解析：**
    -   **默认状态 (True)**：`true != DefaultValue(false)` -> 属性被序列化写入 JSON (`ShowBorder: true`)。JS 读到 `true`。
    -   **用户取消勾选 (False)**：`false == DefaultValue(false)` -> 属性被省略。JS 读到 `undefined`。

    **JS 端实现：**
    ```javascript
    // 此时 JS 逻辑可以非常简单，视 undefined 为 false 即可
    const showBorder = this.CellElement.CellType.ShowBorder || false;
    
    if (showBorder) {
        // ... 渲染边框
    }
    ```

    > **注意**：这种写法可能会引发代码分析器的默认值不一致警告，请忽略该警告，这是为了业务逻辑闭环而做的必要 Hack。

## 10. 第三方库集成：数据处理管道 (Data Pipelines)

在集成如 ECharts, G2, Spreadsheet 等需要特定数据格式的库时，数据转换往往是 Bug 的高发区。

-   **痛点**：初始化时编写了复杂的 `mapping` 逻辑，但在后续通过 `Command` 或 `onRender` 更新数据时，AI 容易直接传递原始 JSON，导致第三方库因为格式不匹配而报错或静默更新失败。
-   **核心原则**：**逻辑复用**。将“数据源 -> 视图模型”的转换逻辑提取为独立的纯函数（Pure Function）。

### 推荐模式

```javascript
class MyChartCellType extends Forguncy.Plugin.CellTypeBase {
    // 1. 提取转换管道
    transformData(rawData) {
        if (!rawData) return [];
        return rawData.map(item => ({
            category: item.Type,
            amount: item.Value
        }));
    }

    onRender(container, renderInfo) {
        // 2. 初始化/全量更新时使用
        const chartData = this.transformData(renderInfo.Value);
        this.chart.source(chartData);
    }

    updateData(newData) {
        // 3. 局部更新逻辑务必经过相同的管道
        const chartData = this.transformData(newData);
        this.chart.changeData(chartData);
    }
}
```

-   **检查清单**：
    -   [ ] 初始化代码中是否有数据转换？
    -   [ ] 更新代码（`updateData`, `onRender`, `onCommand`）是否复用了该转换？
    -   [ ] 转换逻辑是否已提取为独立方法？

## 11. 预设配置 (Preset) 模式：提升复杂组件易用性

当插件包含大量嵌套配置（如多轨道、多曲线、多坐标轴）时，要求用户从原子项开始逐个配置会导致极高的上手门槛和出错率。

-   **核心思路**：引入“业务宏”的概念。在属性设计上提供一个“预设”下拉框，用户选择后，代码内部自动展开为对应的底层原子配置。

### 实现模式 (以多曲线轨道为例)

#### 1. 设计器端 (C#) 定义业务语义属性

```csharp
public enum TrackPreset {
    Custom,      // 用户手动配置
    Lithology,   // 岩性轨道 (预设包含：GR, CALI 曲线)
    Resistivity  // 电阻率轨道 (预设包含：RDEP, RMED 曲线)
}

[DisplayName("轨道预设")]
[ComboProperty]
public TrackPreset Preset { get; set; }
```

#### 2. Web端 (JS) 实现逻辑展开

```javascript
class WellogCellType extends Forguncy.Plugin.CellTypeBase {
    // 内部方法：获取实际运行的原子配置
    getEffectiveConfig() {
        const settings = this.CellElement.CellType;
        
        // 如果是预设模式，返回硬编码的业务组合
        if (settings.Preset === "Lithology") {
            return {
                tracks: [{
                    name: "Lithology",
                    plots: [{ type: "line", field: "GR", color: "red" }, { type: "line", field: "CALI", color: "blue" }]
                }]
            };
        }
        
        // 否则返回用户手动定义的配置
        return settings.CustomConfig;
    }

    onRender(container, renderInfo) {
        const config = this.getEffectiveConfig();
        this.initLibrary(config);
    }
}
```

-   **优点**：
    -   **降低门槛**：业务人员只需选择“岩性轨道”，无需理解什么是 `Plot` 或 `Line`。
    -   **减少错误**：预设配置经过验证，避免了颜色、比例尺等技术参数配错。
    -   **平滑迁移**：保留 `Custom` 选项，允许高级用户在需要时进行精细化调整。

## 12. 默认值 management 一致性：单一真相来源 (SSOT)

在插件开发中，默认值（如默认颜色、默认轨道配置）往往需要在 C#（设计器端显示）和 JS（运行时渲染）中同时存在。

-   **现状痛点**：两端分别硬编码 `defaultColor = "red"`。一旦需要修改，必须两处同步，极易遗漏。
-   **推荐方案**：由 C# 掌控默认值，JS 动态获取。

### 实现模式：C# 序列化传递

#### 1. C# 端定义常量与初始化

```csharp
public class MyPluginCellType : CellType {
    // 1. 定义唯一的默认值常量 (或从 JSON 文件读取)
    private const string DEFAULT_TRACK_CONFIG = "[{\"name\": \"Default\", \"color\": \"#FF0000\"}]";

    // 2. 在构造函数中应用默认值
    public MyPluginCellType() {
        this.TrackConfigs = DEFAULT_TRACK_CONFIG;
    }

    [DisplayName("轨道配置")]
    public string TrackConfigs { get; set; }
}
```

#### 2. JS 端动态读取 (无硬编码)

```javascript
class MyPluginCellType extends Forguncy.Plugin.CellTypeBase {
    onRender(container, renderInfo) {
        // 直接从 CellType 获取值，如果为空则说明 C# 构造函数没跑（理论上不会）
        // 严禁在此处写：const config = settings.TrackConfigs || "[{...}]";
        const configStr = this.CellElement.CellType.TrackConfigs;
        const config = JSON.parse(configStr);
        
        this.renderChart(config);
    }
}
```

-   **核心优势**：
    -   **修改点唯一**：只需要在 C# 端修改一次，前后端同步生效。
    -   **配置透明**：用户在设计器中能看到默认值，而不是看到一个“空”但在运行时却有东西。
    -   **减少 Bug**：消除了由于两端逻辑版本不一致导致的渲染异常。

## 13. 交互幂等性 (Idempotency)：防止状态叠加与内存泄漏

在实现 `RunTimeMethod` 或 `updateData` 时，频繁触发的调用可能导致重复的 DOM 操作或库初始化。

-   **核心风险**：某些第三方库（如 `videx-wellog`）的 `reset()` 或 `setTracks()` 并不总是完全覆盖，可能存在资源释放不彻底或节点累加的问题。
-   **解决方案**：在执行逻辑前，先对比“旧值”与“新值”。

### 实现模式：值对比守卫

```javascript
class MyPluginCellType extends Forguncy.Plugin.CellTypeBase {
    constructor() {
        super();
        this._lastDataJson = null; // 存储上一次渲染的数据快照
    }

    updateData(newData) {
        const currentDataJson = JSON.stringify(newData);
        
        // 1. 幂等性检查：如果数据没变，直接返回
        if (this._lastDataJson === currentDataJson) {
            console.log("[MyPlugin]: Data unchanged, skipping update.");
            return;
        }

        // 2. 执行昂贵的更新操作
        this.performHeavyUpdate(newData);
        
        // 3. 更新快照
        this._lastDataJson = currentDataJson;
    }

    performHeavyUpdate(data) {
        this._container.empty(); // 彻底清理
        this.initLibrary(data);
    }
}
```

-   **适用场景**：
    -   **重置/重载逻辑**：避免用户快速连点或公式高频计算导致的性能崩塌。
    -   **复杂 DOM 操作**：防止生成重复的子元素。
    -   **昂贵计算**：如大数据量转换、3D 渲染初始化。

## 14. 大型插件的代码组织规范：物理拆分与有序加载

当插件功能变得复杂时，单文件（God File）会导致维护成本指数级上升。活字格支持加载多个 JS 文件，我们可以利用这一点实现简单的模块化。

-   **推荐结构**：
    -   `Constants.js`：定义全局常量、枚举。
    -   `Utils.js`：通用工具函数（如数据转换、格式化）。
    -   `Core.js` / `Factory.js`：核心业务逻辑或组件工厂。
    -   `Main.js`：继承自 `CellTypeBase` 或 `CommandBase` 的入口类。

### 实现模式：有序加载 (Ordered Loading)

由于活字格插件环境不支持 ES Modules (import/export)，各文件通过全局变量（或挂载在插件命名空间下）进行通信。

#### 1. 定义命名空间 (Constants.js)

```javascript
// 推荐使用插件 ID 作为命名空间，防止全局污染
var MyPlugin = MyPlugin || {};
MyPlugin.Constants = {
    DEFAULT_COLOR: "red"
};
```

#### 2. 实现入口逻辑 (Main.js)

```javascript
class MyCellType extends Forguncy.Plugin.CellTypeBase {
    onRender(container, renderInfo) {
        // 使用在 Constants.js 中定义的常量
        console.log(MyPlugin.Constants.DEFAULT_COLOR);
    }
}
```

#### 3. 配置加载顺序 (PluginConfig.json)

**关键点**：`javascript` 数组中的顺序即为浏览器加载顺序。被依赖的文件必须排在前面。

```json
{
    "javascript": [
        "Scripts/Constants.js",
        "Scripts/Utils.js",
        "Scripts/Main.js"
    ]
}
```

-   **优势**：
    -   **职责清晰**：开发者可以快速定位到是工具类问题还是业务逻辑问题。
    -   **多人协作**：不同开发者可以负责不同的物理文件，减少 Git 冲突。
    -   **按需加载**：虽然目前活字格是一次性加载，但物理拆分为未来的按需打包打下了基础。


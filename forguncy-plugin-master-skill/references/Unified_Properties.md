# 统一属性指南 (Unified Properties Guide)

本指南涵盖了活字格插件（服务端命令与单元格类型）中常用的属性定义方式及高级配置。

## 1. 基础属性类型 (Basic Types)

### 1.1 字符串 (String)
- **C# 定义**：
  ```csharp
  [DisplayName("文本内容")]
  [TextProperty(Watermark = "请输入...", AcceptsReturn = true)]
  public string MyText { get; set; }
  ```
- **关键点**：`Watermark` 设置水印，`AcceptsReturn` 支持多行，`CanSelectResource` 支持多语言。

### 1.2 数字 (Integer / Double)
- **C# 定义**：
  ```csharp
  [DisplayName("数值")]
  [IntProperty(MinValue = 0, MaxValue = 100)]
  public int MyInt { get; set; }
  ```
- **关键点**：使用 `[IntProperty]` 或 `[DoubleProperty]` 限制取值范围。

### 1.3 布尔值 (Boolean)
- **C# 定义**：
  ```csharp
  [DisplayName("启用")]
  [DefaultValue(true)]
  public bool IsEnabled { get; set; } = true;
  ```
- **安全提醒**：若初始值为 `true`，必须配合 `[DefaultValue(true)]` 特性，否则 `false` 状态无法正确保存。

---

## 2. 选择类属性 (Selection)

### 2.1 枚举与下拉框 (Enum / Dropdown)
- **C# 定义**：
  ```csharp
  public enum MyOptions { A, B, C }

  [DisplayName("选项")]
  public MyOptions Option { get; set; }
  ```
- **前后端同步安全原则**：
  - JS 端严禁使用魔法数字，应定义常量对象映射：`const Options = { A: 0, B: 1 };`
  - 使用 `this.CellElement.CellType.Option` 获取值并与常量对比。

---

## 3. 高级属性 (Advanced)

### 3.1 公式支持 (Formula)
- **C# 定义**：
  ```csharp
  [DisplayName("动态值")]
  [FormulaProperty]
  public object DynamicValue { get; set; }
  ```
- **服务端处理**：`context.EvaluateFormula(DynamicValue)`。
- **前端处理**：`this.evaluateFormulaAsync(this.CellElement.CellType.DynamicValue)`。

### 3.2 列表与对象 (Object / List)
- **C# 定义**：
  ```csharp
  [DisplayName("配置列表")]
  public List<MyItem> Items { get; set; }
  ```
- **注意**：复杂对象会自动序列化为 JSON 字符串传递给前端。

---

## 4. 开发建议
- **简洁性**：优先使用基础类型，仅在必要时引入复杂对象。
- **安全性**：对所有属性值进行防御性编程，处理 `null` 或 `undefined` 的情况。

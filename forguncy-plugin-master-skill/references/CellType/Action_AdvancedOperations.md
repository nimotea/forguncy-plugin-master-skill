# 添加单元格操作 - 高级单元格操作 (Advanced Cell Operations)

## 参考资料
[添加高级单元格操作 - 活字格V11帮助文档](https://www.grapecity.com.cn/solutions/huozige/help/docs/plugindevelopment/plugindevelop/developcelltypeplugin/addcellaction/addadvancedcelloperations)

## 概述
定义自定义的方法（操作），供“操作单元格”命令调用。支持传递参数和返回值。

## 1. 基础操作 (无参)
**C#**:
```csharp
public class MyPluginCellType : CellType
{
    [RunTimeMethod]
    public void MyOperation() { }
}
```

**JS**:
```javascript
class MyPluginCellType extends Forguncy.Plugin.CellTypeBase {
    MyOperation() {
        alert("被调用");
    }
}
```

## 2. 带参数的操作
**C#**:
```csharp
[RunTimeMethod]
public void ShowMessage(
    [ItemDisplayName("标题")] string title,
    [ItemDisplayName("内容")] string content
) { }
```

**JS**:
```javascript
ShowMessage(title, content) {
    alert(title + ": " + content);
}
```

## 3. 带返回值的操作
**C#**:
```csharp
[RunTimeMethod]
public GetInfoResult GetInfo() { return null; }

public class GetInfoResult
{
    [DisplayName("当前值")]
    public string CurrentValue { get; set; }
}
```

**JS**:
```javascript
GetInfo() {
    return {
        CurrentValue: this.getValueFromElement()
    };
}
```

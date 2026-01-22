# 添加属性 - 对象列表属性 (Object List Property)

## 参考资料
[对象列表属性 - 活字格V11帮助文档](https://www.grapecity.com.cn/solutions/huozige/help/docs/plugindevelopment/plugindevelop/developcelltypeplugin/addproperty/objectlistproperty)

## 概述
用于管理复杂对象的列表。设计器提供增删改查的 UI。

## 基础用法 ([ObjectListProperty])
列表项类型必须实现 `INamedObject` 接口（用于显示列表项名称）。

```csharp
public class MyPluginCellType : CellType
{
    [ObjectListProperty(ItemType = typeof(ColumnConfig))]
    public List<INamedObject> Columns { get; set; } = new List<INamedObject>();
}

public class ColumnConfig : ObjectPropertyBase, INamedObject
{
    [DisplayName("列名")]
    public string Name { get; set; } // 实现 INamedObject
    
    [DisplayName("宽度")]
    public int Width { get; set; }
}
```

## JS 处理逻辑
在 JS 中，列表属性会作为数组传递。

```javascript
class MyPluginCellType extends Forguncy.Plugin.CellTypeBase {
    createContent() {
        const columns = this.CellElement.CellType.Columns;
        const container = $("<div></div>");
        
        // 遍历列表
        for (const col of columns) {
            container.append(`<div>${col.Name}: ${col.Width}px</div>`);
        }
        
        return container;
    }
}
```
